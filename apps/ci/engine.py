import math
import base64
import json
import cv2
import numpy as np

def clamp(value, low=0.0, high=100.0):
    return max(low, min(high, float(value)))

def safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default

def encode_image(img, quality=92):
    """
    OpenCV image -> base64 JPEG
    """
    ok, buffer = cv2.imencode(
        ".jpg",
        img,
        [cv2.IMWRITE_JPEG_QUALITY, quality]
    )

    if not ok:
        return ""

    return base64.b64encode(buffer.tobytes()).decode("utf-8")

def resize_keep_ratio(img, max_w=1280, max_h=900):
    h, w = img.shape[:2]

    scale = min(
        max_w / max(w, 1),
        max_h / max(h, 1),
        1.0
    )

    if scale == 1.0:
        return img.copy()

    return cv2.resize(
        img,
        (int(w * scale), int(h * scale)),
        interpolation=cv2.INTER_AREA
    )

def analyze_exposure(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    total = gray.size

    highlight_clip = float(np.sum(gray >= 250) / total * 100)
    shadow_clip = float(np.sum(gray <= 8) / total * 100)

    mean_luma = float(np.mean(gray))
    median_luma = float(np.median(gray))

    p05 = float(np.percentile(gray, 5))
    p95 = float(np.percentile(gray, 95))

    dynamic_range = p95 - p05

    # exposure score
    exposure_score = 100.0

    if highlight_clip > 5:
        exposure_score -= min(35, (highlight_clip - 5) * 4)

    if shadow_clip > 8:
        exposure_score -= min(25, (shadow_clip - 8) * 2)

    if mean_luma < 55:
        exposure_score -= 10

    if mean_luma > 205:
        exposure_score -= 10

    exposure_score = clamp(exposure_score)

    return {
        "highlight_clip": round(highlight_clip, 2),
        "shadow_clip": round(shadow_clip, 2),
        "mean_luma": round(mean_luma, 1),
        "median_luma": round(median_luma, 1),
        "p05": round(p05, 1),
        "p95": round(p95, 1),
        "dynamic_range": round(dynamic_range, 1),
        "score": round(exposure_score)
    }

def detect_horizon(img):
    """
    Robust horizon estimation.

    Returns:
        angle
        y
        confidence
        line
    """

    h, w = img.shape[:2]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    edges = cv2.Canny(gray, 50, 140)

    # 中上部区域寻找近水平线
    y_start = int(h * 0.20)
    y_end = int(h * 0.72)

    roi = edges[y_start:y_end, :]

    lines = cv2.HoughLinesP(
        roi,
        1,
        np.pi / 180,
        threshold=max(35, int(w * 0.04)),
        minLineLength=max(60, int(w * 0.12)),
        maxLineGap=30
    )

    candidates = []

    if lines is not None:

        for item in lines:
            arr = np.asarray(item).reshape(-1)

            if arr.size != 4:
                continue

            x1, y1, x2, y2 = map(float, arr)

            y1 += y_start
            y2 += y_start

            dx = x2 - x1
            dy = y2 - y1

            length = math.sqrt(dx * dx + dy * dy)

            if length < w * 0.10:
                continue

            angle = math.degrees(math.atan2(dy, dx))

            # 接近水平
            if abs(angle) <= 8.0:

                center_y = (y1 + y2) / 2

                # 湖面 / 山脚 / 建筑边缘附近更加可信
                if h * 0.28 <= center_y <= h * 0.70:
                    candidates.append(
                        (angle, center_y, length, (x1, y1, x2, y2))
                    )

    if not candidates:
        return {
            "angle": 0.0,
            "y": int(h * 0.50),
            "confidence": 28,
            "line": None
        }

    # 长线优先，同时避免极端值
    candidates.sort(
        key=lambda x: x[2],
        reverse=True
    )

    selected = candidates[:min(12, len(candidates))]

    angles = np.array([x[0] for x in selected], dtype=np.float32)
    ys = np.array([x[1] for x in selected], dtype=np.float32)

    weights = np.array(
        [x[2] for x in selected],
        dtype=np.float32
    )

    angle = float(
        np.average(angles, weights=weights)
    )

    horizon_y = float(
        np.average(ys, weights=weights)
    )

    # 根据候选数量 + 线长度估计置信度
    confidence = 35 + min(45, len(candidates) * 4)

    if max(weights) > w * 0.45:
        confidence += 10

    confidence = int(clamp(confidence, 20, 95))

    best = selected[0][3]

    return {
        "angle": round(angle, 2),
        "y": int(horizon_y),
        "confidence": confidence,
        "line": tuple(int(v) for v in best)
    }

def line_intersection(line1, line2):
    x1, y1, x2, y2 = map(float, line1)
    x3, y3, x4, y4 = map(float, line2)

    den = (
        (x1 - x2) * (y3 - y4)
        -
        (y1 - y2) * (x3 - x4)
    )

    if abs(den) < 1e-6:
        return None

    px = (
        (x1 * y2 - y1 * x2) * (x3 - x4)
        -
        (x1 - x2) * (x3 * y4 - y3 * x4)
    ) / den

    py = (
        (x1 * y2 - y1 * x2) * (y3 - y4)
        -
        (y1 - y2) * (x3 * y4 - y3 * x4)
    ) / den

    return px, py

def detect_vanishing_point(img, horizon):
    """
    Estimate perspective VP using strong lower-image lines.

    This is intentionally deterministic and transparent for demo purposes.
    """

    h, w = img.shape[:2]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    edges = cv2.Canny(gray, 45, 130)

    mask = np.zeros_like(edges)

    # lower 70% of image
    cv2.rectangle(
        mask,
        (0, int(h * 0.30)),
        (w, h),
        255,
        -1
    )

    edges = cv2.bitwise_and(edges, mask)

    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi / 180,
        threshold=max(30, int(w * 0.025)),
        minLineLength=max(50, int(w * 0.08)),
        maxLineGap=35
    )

    candidates = []

    if lines is not None:

        for item in lines:

            arr = np.asarray(item).reshape(-1)

            if arr.size != 4:
                continue

            x1, y1, x2, y2 = map(float, arr)

            dx = x2 - x1
            dy = y2 - y1

            length = math.hypot(dx, dy)

            if length < w * 0.08:
                continue

            angle = math.degrees(math.atan2(dy, dx))

            # 过滤掉近水平线
            if abs(angle) < 8:
                continue

            # 过滤垂直线
            if abs(abs(angle) - 90) < 12:
                continue

            candidates.append(
                (x1, y1, x2, y2, length, angle)
            )

    if len(candidates) < 2:
        return {
            "x": int(w * 0.50),
            "y": int(horizon["y"]),
            "confidence": 25
        }

    # 最长的一批线
    candidates.sort(
        key=lambda x: x[4],
        reverse=True
    )

    selected = candidates[:20]

    intersections = []

    for i in range(len(selected)):
        for j in range(i + 1, len(selected)):

            l1 = selected[i][:4]
            l2 = selected[j][:4]

            # 两条线角度差太小
            a1 = selected[i][5]
            a2 = selected[j][5]

            if abs(a1 - a2) < 12:
                continue

            point = line_intersection(l1, l2)

            if point is None:
                continue

            px, py = point

            # VP不能离图像太离谱
            if (
                -w * 0.5 <= px <= w * 1.5
                and
                -h * 0.3 <= py <= h * 1.3
            ):
                intersections.append(
                    (px, py)
                )

    if not intersections:
        return {
            "x": int(w * 0.50),
            "y": int(horizon["y"]),
            "confidence": 30
        }

    points = np.array(
        intersections,
        dtype=np.float32
    )

    # 中位数比平均数更抗异常值
    vx = float(np.median(points[:, 0]))
    vy = float(np.median(points[:, 1]))

    # VP通常与地平线接近
    target_y = float(horizon["y"])

    vy = 0.70 * vy + 0.30 * target_y

    # confidence
    count_score = min(35, len(intersections) * 1.5)

    center_distance = abs(vx - w / 2) / (w / 2)

    center_score = max(
        0,
        25 * (1 - min(center_distance, 1))
    )

    confidence = int(
        clamp(
            25 + count_score + center_score,
            20,
            92
        )
    )

    return {
        "x": int(vx),
        "y": int(vy),
        "confidence": confidence
    }

def analyze_visual_flow(img):
    h, w = img.shape[:2]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(
        cv2.GaussianBlur(gray, (5, 5), 0),
        60,
        150
    )

    # 分区计算边缘密度
    regions = {
        "top": edges[:h // 3, :],
        "middle": edges[h // 3:2 * h // 3, :],
        "bottom": edges[2 * h // 3:, :]
    }

    densities = {}

    for name, region in regions.items():
        densities[name] = float(
            np.mean(region > 0)
        )

    overall = float(np.mean(edges > 0))

    # 左右视觉复杂度
    left = edges[:, :w // 2]
    right = edges[:, w // 2:]

    left_density = float(np.mean(left > 0))
    right_density = float(np.mean(right > 0))

    balance = 100 - min(
        45,
        abs(left_density - right_density) * 900
    )

    # 前景通常边缘更丰富
    depth_signal = (
        densities["bottom"] * 0.50
        +
        densities["middle"] * 0.30
        +
        densities["top"] * 0.20
    )

    depth_score = clamp(
        55 + depth_signal * 300
    )

    flow_score = clamp(
        62
        +
        overall * 280
        +
        abs(densities["bottom"] - densities["top"]) * 90
    )

    return {
        "flow_score": int(round(flow_score)),
        "balance_score": int(round(balance)),
        "depth_score": int(round(depth_score)),
        "edge_density": round(overall * 100, 2),
        "left_density": round(left_density * 100, 2),
        "right_density": round(right_density * 100, 2),
        "regions": {
            k: round(v * 100, 2)
            for k, v in densities.items()
        }
    }

def analyze_thirds(img):
    h, w = img.shape[:2]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Sobel energy
    gx = cv2.Sobel(
        gray,
        cv2.CV_32F,
        1,
        0,
        ksize=3
    )

    gy = cv2.Sobel(
        gray,
        cv2.CV_32F,
        0,
        1,
        ksize=3
    )

    mag = cv2.magnitude(gx, gy)

    points = [
        (w / 3, h / 3),
        (2 * w / 3, h / 3),
        (w / 3, 2 * h / 3),
        (2 * w / 3, 2 * h / 3)
    ]

    scores = []

    radius = max(15, int(min(w, h) * 0.035))

    for px, py in points:

        x1 = max(0, int(px - radius))
        x2 = min(w, int(px + radius))
        y1 = max(0, int(py - radius))
        y2 = min(h, int(py + radius))

        region = mag[y1:y2, x1:x2]

        if region.size:
            scores.append(float(np.mean(region)))

    if not scores:
        return 65

    normalized = np.mean(scores)

    score = 55 + min(
        35,
        normalized / 12
    )

    return int(clamp(score))

def golden_ratio_score(img):
    h, w = img.shape[:2]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # visual energy map
    blur = cv2.GaussianBlur(gray, (0, 0), 5)

    detail = cv2.absdiff(gray, blur)

    # golden ratio positions
    phi = 0.618

    gx = int(w * phi)
    gy = int(h * phi)

    radius = int(min(w, h) * 0.045)

    x1 = max(0, gx - radius)
    x2 = min(w, gx + radius)
    y1 = max(0, gy - radius)
    y2 = min(h, gy + radius)

    roi = detail[y1:y2, x1:x2]

    energy = float(np.mean(roi)) if roi.size else 0

    return int(
        clamp(
            55 + energy * 2.0,
            40,
            96
        )
    )

def calculate_composition_score(
    exposure,
    horizon,
    flow,
    thirds,
    depth
):
    horizon_score = clamp(
        100 - abs(horizon["angle"]) * 8
    )

    perspective_score = horizon["confidence"]

    visual_balance = flow["balance_score"]

    tonal = exposure["score"]

    # 权重
    overall = (
        flow["flow_score"] * 0.22
        +
        visual_balance * 0.17
        +
        perspective_score * 0.13
        +
        horizon_score * 0.15
        +
        tonal * 0.14
        +
        thirds * 0.09
        +
        depth * 0.10
    )

    return int(round(clamp(overall)))

def generate_insights(
    score,
    exposure,
    horizon,
    vp,
    flow,
    thirds,
    depth
):
    insights = []
    recommendations = []

    # Visual flow
    if flow["flow_score"] >= 78:
        insights.append(
            "Foreground geometry creates a strong visual entry path into the scene."
        )
    else:
        insights.append(
            "The frame contains identifiable visual structure, but the eye path could be strengthened."
        )

    # Depth
    if depth >= 85:
        insights.append(
            "Foreground, midground and distant layers produce convincing depth separation."
        )
    else:
        insights.append(
            "Depth layering is present, although foreground-to-background separation could be stronger."
        )

    # Horizon
    if abs(horizon["angle"]) <= 1.5:
        insights.append(
            "Horizon alignment is visually stable and requires minimal correction."
        )
    else:
        recommendations.append(
            f"Consider a subtle {abs(horizon['angle']):.1f}° horizon correction."
        )

    # Exposure
    if exposure["highlight_clip"] < 2:
        insights.append(
            "Highlight retention is strong with limited clipping in bright regions."
        )
    else:
        recommendations.append(
            "Protect bright cloud detail by slightly reducing highlight exposure."
        )

    # thirds
    if thirds >= 78:
        insights.append(
            "Key visual energy is reasonably compatible with a rule-of-thirds structure."
        )
    else:
        recommendations.append(
            "A tighter crop around one of the primary thirds intersections may improve subject hierarchy."
        )

    # Perspective
    if vp["confidence"] >= 70:
        insights.append(
            "Perspective structure is sufficiently coherent for a reliable vanishing-point estimate."
        )
    else:
        recommendations.append(
            "Perspective confidence is moderate; avoid treating the estimated vanishing point as exact."
        )

    if not recommendations:
        recommendations.append(
            "Current structure is strong. Preserve the existing horizon and tonal balance during post-processing."
        )

    if score >= 88:
        status = "EXCELLENT STRUCTURAL CONTROL"
    elif score >= 78:
        status = "STRONG COMPOSITIONAL STRUCTURE"
    elif score >= 68:
        status = "SOLID BUT REFINABLE"
    else:
        status = "COMPOSITION NEEDS REFINEMENT"

    return {
        "status": status,
        "insights": insights[:4],
        "recommendations": recommendations[:3]
    }

def draw_grid(img):
    result = img.copy()

    h, w = result.shape[:2]

    # subtle thirds grid
    color = (95, 125, 125)

    x1 = int(w / 3)
    x2 = int(2 * w / 3)

    y1 = int(h / 3)
    y2 = int(2 * h / 3)

    overlay = result.copy()

    for x in [x1, x2]:
        cv2.line(
            overlay,
            (x, 0),
            (x, h),
            color,
            1,
            cv2.LINE_AA
        )

    for y in [y1, y2]:
        cv2.line(
            overlay,
            (0, y),
            (w, y),
            color,
            1,
            cv2.LINE_AA
        )

    # subtle blend
    result = cv2.addWeighted(
        overlay,
        0.45,
        result,
        0.55,
        0
    )

    # intersection markers
    points = [
        (x1, y1),
        (x2, y1),
        (x1, y2),
        (x2, y2)
    ]

    for x, y in points:
        cv2.circle(
            result,
            (x, y),
            4,
            (150, 170, 160),
            1,
            cv2.LINE_AA
        )

    return result

def draw_horizon(img, horizon):
    result = img.copy()

    if not horizon.get("line"):
        return result

    x1, y1, x2, y2 = horizon["line"]

    # black shadow
    cv2.line(
        result,
        (x1, y1),
        (x2, y2),
        (0, 0, 0),
        5,
        cv2.LINE_AA
    )

    # technical line
    cv2.line(
        result,
        (x1, y1),
        (x2, y2),
        (80, 220, 150),
        2,
        cv2.LINE_AA
    )

    return result

def draw_vanishing_point(img, vp):
    result = img.copy()

    x = int(vp["x"])
    y = int(vp["y"])

    h, w = result.shape[:2]

    if not (
        -w <= x <= 2 * w
        and
        -h <= y <= 2 * h
    ):
        return result

    # only display if reasonably close
    x_draw = max(0, min(w - 1, x))
    y_draw = max(0, min(h - 1, y))

    cv2.circle(
        result,
        (x_draw, y_draw),
        10,
        (0, 0, 0),
        3,
        cv2.LINE_AA
    )

    cv2.circle(
        result,
        (x_draw, y_draw),
        7,
        (80, 230, 170),
        1,
        cv2.LINE_AA
    )

    cv2.line(
        result,
        (x_draw - 16, y_draw),
        (x_draw + 16, y_draw),
        (80, 230, 170),
        1,
        cv2.LINE_AA
    )

    cv2.line(
        result,
        (x_draw, y_draw - 16),
        (x_draw, y_draw + 16),
        (80, 230, 170),
        1,
        cv2.LINE_AA
    )

    return result

def draw_visual_flow(img):
    """
    Detect strong lower-image edges and draw a restrained leading-line hint.
    """

    result = img.copy()

    h, w = result.shape[:2]

    gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(
        cv2.GaussianBlur(gray, (5, 5), 0),
        70,
        160
    )

    # Focus on lower half
    roi = edges[int(h * 0.50):, :]

    lines = cv2.HoughLinesP(
        roi,
        1,
        np.pi / 180,
        threshold=max(25, int(w * 0.02)),
        minLineLength=max(60, int(w * 0.10)),
        maxLineGap=40
    )

    if lines is None:
        return result

    candidates = []

    for item in lines:

        arr = np.asarray(item).reshape(-1)

        if arr.size != 4:
            continue

        x1, y1, x2, y2 = map(int, arr)

        y1 += int(h * 0.50)
        y2 += int(h * 0.50)

        dx = x2 - x1
        dy = y2 - y1

        length = math.hypot(dx, dy)

        if length < w * 0.12:
            continue

        angle = math.degrees(math.atan2(dy, dx))

        # leading lines often have moderate slopes
        if 8 < abs(angle) < 70:

            # favor lower part
            if max(y1, y2) > h * 0.70:
                candidates.append(
                    (length, (x1, y1, x2, y2))
                )

    candidates.sort(
        key=lambda x: x[0],
        reverse=True
    )

    # 最多画两条
    for _, line in candidates[:2]:

        x1, y1, x2, y2 = line

        cv2.line(
            result,
            (x1, y1),
            (x2, y2),
            (20, 20, 20),
            5,
            cv2.LINE_AA
        )

        cv2.line(
            result,
            (x1, y1),
            (x2, y2),
            (80, 190, 210),
            2,
            cv2.LINE_AA
        )

    return result

def create_analysis_image(img, horizon, vp):
    """
    Create professional restrained overlay.
    """

    result = img.copy()

    result = draw_grid(result)

    result = draw_horizon(
        result,
        horizon
    )

    result = draw_visual_flow(result)

    result = draw_vanishing_point(
        result,
        vp
    )

    return result

def analyze_image(img):
    h, w = img.shape[:2]

    exposure = analyze_exposure(img)

    horizon = detect_horizon(img)

    vp = detect_vanishing_point(
        img,
        horizon
    )

    flow = analyze_visual_flow(img)

    thirds = analyze_thirds(img)

    golden = golden_ratio_score(img)

    depth = flow["depth_score"]

    score = calculate_composition_score(
        exposure,
        horizon,
        flow,
        thirds,
        depth
    )

    insights = generate_insights(
        score,
        exposure,
        horizon,
        vp,
        flow,
        thirds,
        depth
    )

    annotated = create_analysis_image(
        img,
        horizon,
        vp
    )

    return {
        "score": score,

        "status": insights["status"],

        "visual_flow": flow["flow_score"],
        "visual_balance": flow["balance_score"],
        "perspective": vp["confidence"],
        "horizon_control": int(
            clamp(
                100 - abs(horizon["angle"]) * 8
            )
        ),
        "tonal_exposure": exposure["score"],
        "depth": depth,
        "thirds": thirds,
        "golden_ratio": golden,

        "horizon": {
            "angle": horizon["angle"],
            "y": horizon["y"],
            "confidence": horizon["confidence"]
        },

        "vanishing_point": {
            "x": vp["x"],
            "y": vp["y"],
            "confidence": vp["confidence"]
        },

        "exposure": exposure,

        "insights": insights["insights"],
        "recommendations": insights["recommendations"],

        "annotated_image": encode_image(
            annotated
        )
    }

def analyze_upload(path):
    img = cv2.imread(path)
    if img is None:
        raise ValueError("无法读取图片，请选择 JPG、PNG、WebP 或 BMP 图片。")
    img = resize_keep_ratio(img, max_w=1800, max_h=1400)
    result = analyze_image(img)
    h, w = img.shape[:2]
    result["resolution"] = f"{w} × {h}"
    result["aspect_ratio"] = f"{w / h:.2f}:1"
    return json.dumps(result, ensure_ascii=False, allow_nan=False)
