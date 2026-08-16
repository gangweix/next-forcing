const cases = [
  {
    prompt: "The video presents a cinematic view of the lunar surface from a low-altitude perspective. The foreground and midground are dominated by a vast, desolate landscape of grey, rocky terrain characterized by numerous craters, ridges, and undulating hills. The lighting is harsh and directional, casting deep, sharp shadows that emphasize the rough, granular texture of the moon's surface. In the upper right portion of the frame, the Earth is visible as a bright, blue-and-white celestial body against the pitch-black void of space. The atmosphere is quiet, cold, and awe-inspiring, capturing the isolation of the lunar environment.",
    slug: "lunar-surface-earthrise"
  },
  {
    prompt: "In a dimly lit indoor setting with a cool blue and purple ambient glow, a person is seated at a wooden desk. The person, wearing a black turtleneck and a black smartwatch, is focused on a mobile transaction. They hold a dark green smartphone in their left hand and a silver credit card in their right hand, carefully aligning the card with the phone's screen. In the foreground, a small potted plant is visible but out of focus, while a tablet with a keyboard and some papers are scattered on the desk in the background. The atmosphere is quiet and concentrated, suggesting a late-night or evening work or shopping session.",
    slug: "night-mobile-payment"
  },
  {
    prompt: "A close-up shot of a young man with dark hair in a dimly lit, rustic environment. He is wearing a dark jacket over a light-colored shirt that is heavily stained with dark red blood around the collar and chest. The man is looking downward with a pained and distressed expression, his mouth moving as if he is speaking or gasping. The background is out of focus, showing what appears to be a stone or wooden wall, contributing to a somber and tense atmosphere.",
    slug: "distressed-man-closeup"
  },
  {
    prompt: "The video captures a rural scene on a hillside under an overcast sky. A man, carrying a massive bundle of dried grass or hay on his back, walks steadily along a dirt path. In the background, there are several modest houses, including one with a white wall and a rusted metal roof, and another with a corrugated metal side. The surrounding landscape consists of a steep, green hillside with scattered trees and shrubs. The atmosphere is quiet and industrious, typical of a rural agricultural setting.",
    slug: "rural-hay-carrier"
  },
  {
    prompt: "A close-up shot captures a person's hands holding a modern smartphone and a black credit card. The person is wearing a crisp white button-down shirt, and the background is softly blurred, suggesting an indoor setting like a living room. The lighting is bright and natural, creating a clean and professional atmosphere. The person holds the smartphone in their left hand on the left side of the frame and the credit card in their right hand on the right side, appearing to be in the middle of an online transaction or data entry process.",
    slug: "phone-card-payment"
  },
  {
    prompt: "A person with vibrant green hair is riding a yellow motorcycle down a long, straight asphalt road in a suburban setting. The road is cracked and weathered, with several red bloodstains scattered across its surface. On the left side of the road, a heavily damaged, rusted red pickup truck is parked. The surrounding environment features various two-story houses with gabled roofs, some showing signs of decay or damage. The sky is bright and overcast, casting a flat, even light over the scene, which has a post-apocalyptic or survivalist atmosphere.",
    slug: "motorcycle-suburban-road"
  }
];

const robotwinCurvePanels = [
  {
    title: "12 FPS · Clean",
    yTicks: [75, 80, 85, 90, 95],
    baseline: [74.0, 85.2, 87.8, 90.8, 92.3, 91.3, 92.8, 92.9, 93.1, 92.8],
    ours: [84.9, 90.0, 91.5, 92.3, 93.3, 94.3, 93.1, 93.4, 94.2, 94.1]
  },
  {
    title: "12 FPS · Random",
    yTicks: [75, 80, 85, 90, 95],
    baseline: [73.5, 82.2, 85.0, 88.3, 88.9, 89.4, 89.3, 91.2, 91.4, 91.8],
    ours: [80.6, 85.4, 85.8, 90.5, 89.8, 91.5, 89.6, 91.5, 91.6, 93.5]
  },
  {
    title: "50 FPS · Clean",
    yTicks: [50, 60, 70, 80, 90],
    baseline: [45.5, 64.8, 69.6, 78.5, 79.0, 81.2, 82.4, 83.8, 87.4, 88.6],
    ours: [70.2, 80.5, 85.2, 87.4, 87.6, 90.0, 90.9, 91.5, 91.7, 91.8]
  },
  {
    title: "50 FPS · Random",
    yTicks: [30, 45, 60, 75, 90],
    baseline: [31.9, 54.7, 59.8, 69.4, 70.7, 75.6, 79.2, 80.4, 84.5, 85.2],
    ours: [61.6, 77.6, 80.2, 85.0, 85.4, 86.8, 89.9, 88.4, 89.6, 90.5],
    annotate: true
  }
];

const robotwinSteps = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50];

const fvdCurvePanels = [
  {
    title: "Test Set 1",
    yTicks: [100, 150, 200, 250, 300, 350],
    baseline: [353, 296, 288, 285, 225],
    ours: [143, 115, 103, 101, 94]
  },
  {
    title: "Test Set 2",
    yTicks: [100, 125, 150, 175, 200, 225],
    baseline: [227, 224, 231, 212, 204],
    ours: [124, 111, 114, 110, 97]
  }
];

const fvdSteps = [10, 20, 30, 40, 50];

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function renderRobotwinCurveChart() {
  const container = document.querySelector("#robotwin-curve-chart");
  if (!container) return;

  const plot = { left: 43, top: 31, width: 184, height: 116 };
  const xDomain = { min: 1.25, max: 52.25 };
  const xTicks = [10, 20, 30, 40, 50];
  const xFor = (step) => plot.left + ((step - xDomain.min) / (xDomain.max - xDomain.min)) * plot.width;
  const pathFrom = (points) => points.map((point, index) => `${index ? "L" : "M"}${point.x.toFixed(1)} ${point.y.toFixed(1)}`).join(" ");

  const svgs = robotwinCurvePanels.map((panel, panelIndex) => {
    const values = panel.baseline.concat(panel.ours);
    let minY = Math.min(...values);
    let maxY = Math.max(...values);
    const pad = Math.max(2, (maxY - minY) * 0.08);
    minY = panel.annotate ? minY - pad - 6 : minY - pad;
    maxY = panel.annotate ? maxY + pad + 4 : maxY + pad;
    const yFor = (value) => plot.top + (1 - (value - minY) / (maxY - minY)) * plot.height;

    const basePoints = robotwinSteps.map((step, index) => ({ x: xFor(step), y: yFor(panel.baseline[index]) }));
    const ourPoints = robotwinSteps.map((step, index) => ({ x: xFor(step), y: yFor(panel.ours[index]) }));
    const fillPath = `${pathFrom(ourPoints)} ${pathFrom(basePoints.slice().reverse()).replace("M", "L")} Z`;
    const basePath = pathFrom(basePoints);
    const ourPath = pathFrom(ourPoints);

    const grid = panel.yTicks.map((tick) => {
      const y = yFor(tick);
      return `
        <line class="curve-grid-line" x1="${plot.left}" y1="${y.toFixed(1)}" x2="${plot.left + plot.width}" y2="${y.toFixed(1)}"></line>
        <text class="curve-y-tick" x="${plot.left - 8}" y="${(y + 4).toFixed(1)}">${tick}</text>
      `;
    }).join("");

    const xLabels = xTicks.map((tick) => {
      const x = xFor(tick);
      return `
        <line class="curve-x-tick" x1="${x.toFixed(1)}" y1="${plot.top + plot.height}" x2="${x.toFixed(1)}" y2="${plot.top + plot.height + 4}"></line>
        <text class="curve-x-label" x="${x.toFixed(1)}" y="${plot.top + plot.height + 20}">${tick}k</text>
      `;
    }).join("");

    const baseMarkers = basePoints.map((point) => (
      `<circle class="curve-marker-base" cx="${point.x.toFixed(1)}" cy="${point.y.toFixed(1)}" r="4.1"></circle>`
    )).join("");
    const ourMarkers = ourPoints.map((point) => (
      `<rect class="curve-marker-ours" x="${(point.x - 4).toFixed(1)}" y="${(point.y - 4).toFixed(1)}" width="8" height="8" rx="1.5"></rect>`
    )).join("");

    const annotation = panel.annotate ? `
      <g class="curve-annotation">
        <line x1="${xFor(5).toFixed(1)}" y1="${yFor(31.9).toFixed(1)}" x2="${xFor(5).toFixed(1)}" y2="${yFor(61.6).toFixed(1)}"></line>
        <path d="M${(xFor(5) - 3).toFixed(1)} ${yFor(31.9).toFixed(1)} L${xFor(5).toFixed(1)} ${(yFor(31.9) + 5).toFixed(1)} L${(xFor(5) + 3).toFixed(1)} ${yFor(31.9).toFixed(1)}"></path>
        <path d="M${(xFor(5) - 3).toFixed(1)} ${yFor(61.6).toFixed(1)} L${xFor(5).toFixed(1)} ${(yFor(61.6) - 5).toFixed(1)} L${(xFor(5) + 3).toFixed(1)} ${yFor(61.6).toFixed(1)}"></path>
        <rect x="${(xFor(5) + 6).toFixed(1)}" y="${((yFor(31.9) + yFor(61.6)) / 2 - 10).toFixed(1)}" width="42" height="18" rx="5"></rect>
        <text x="${(xFor(5) + 27).toFixed(1)}" y="${((yFor(31.9) + yFor(61.6)) / 2 + 3.5).toFixed(1)}">+29.7</text>
        <line x1="${xFor(20).toFixed(1)}" y1="${yFor(85).toFixed(1)}" x2="${xFor(45).toFixed(1)}" y2="${yFor(85).toFixed(1)}"></line>
        <path d="M${xFor(20).toFixed(1)} ${yFor(85).toFixed(1)} L${(xFor(20) + 6).toFixed(1)} ${(yFor(85) - 3).toFixed(1)} L${(xFor(20) + 6).toFixed(1)} ${(yFor(85) + 3).toFixed(1)} Z"></path>
        <path d="M${xFor(45).toFixed(1)} ${yFor(85).toFixed(1)} L${(xFor(45) - 6).toFixed(1)} ${(yFor(85) - 3).toFixed(1)} L${(xFor(45) - 6).toFixed(1)} ${(yFor(85) + 3).toFixed(1)} Z"></path>
        <rect x="${(xFor(32.5) - 37).toFixed(1)}" y="${(yFor(85) + 9).toFixed(1)}" width="74" height="18" rx="5"></rect>
        <text x="${xFor(32.5).toFixed(1)}" y="${(yFor(85) + 22.5).toFixed(1)}">2.3x faster</text>
      </g>
    ` : "";

    const yAxisLabel = panelIndex === 0 ? `<text class="curve-axis-label-y" transform="translate(10 91) rotate(-90)">Success Rate (%)</text>` : "";

    return `
      <svg class="curve-panel" viewBox="0 0 260 194" aria-label="${panel.title}">
        <title>${panel.title}</title>
        <text class="curve-title" x="135" y="18">${panel.title}</text>
        ${grid}
        <line class="curve-axis" x1="${plot.left}" y1="${plot.top + plot.height}" x2="${plot.left + plot.width}" y2="${plot.top + plot.height}"></line>
        <line class="curve-axis" x1="${plot.left}" y1="${plot.top}" x2="${plot.left}" y2="${plot.top + plot.height}"></line>
        ${xLabels}
        ${yAxisLabel}
        <text class="curve-axis-label-x" x="135" y="190">Training Steps</text>
        <path class="curve-gap" d="${fillPath}"></path>
        <path class="curve-line-base" d="${basePath}"></path>
        <path class="curve-line-ours" d="${ourPath}"></path>
        ${baseMarkers}
        ${ourMarkers}
        ${annotation}
      </svg>
    `;
  }).join("");

  container.innerHTML = `
    <div class="curve-top-legend" aria-label="Curve legend">
      <span><i class="legend-line legend-line-base"></i><i class="legend-dot legend-dot-base"></i>LingBot-VA</span>
      <span><i class="legend-line legend-line-ours"></i><i class="legend-dot legend-dot-ours"></i>Next Forcing (Ours)</span>
    </div>
    <div class="curve-panel-grid">${svgs}</div>
  `;
}

function renderFvdCurveChart() {
  const container = document.querySelector("#fvd-curve-chart");
  if (!container) return;

  const plot = { left: 50, top: 33, width: 204, height: 124 };
  const xDomain = { min: 8, max: 52 };
  const xTicks = [10, 20, 30, 40, 50];
  const xFor = (step) => plot.left + ((step - xDomain.min) / (xDomain.max - xDomain.min)) * plot.width;
  const pathFrom = (points) => points.map((point, index) => `${index ? "L" : "M"}${point.x.toFixed(1)} ${point.y.toFixed(1)}`).join(" ");

  const svgs = fvdCurvePanels.map((panel, panelIndex) => {
    const values = panel.baseline.concat(panel.ours);
    let minY = Math.min(...values);
    let maxY = Math.max(...values);
    const pad = Math.max(8, (maxY - minY) * 0.08);
    minY -= pad;
    maxY += pad;
    const yFor = (value) => plot.top + (1 - (value - minY) / (maxY - minY)) * plot.height;

    const basePoints = fvdSteps.map((step, index) => ({ x: xFor(step), y: yFor(panel.baseline[index]) }));
    const ourPoints = fvdSteps.map((step, index) => ({ x: xFor(step), y: yFor(panel.ours[index]) }));
    const fillPath = `${pathFrom(ourPoints)} ${pathFrom(basePoints.slice().reverse()).replace("M", "L")} Z`;

    const grid = panel.yTicks.map((tick) => {
      const y = yFor(tick);
      return `
        <line class="curve-grid-line" x1="${plot.left}" y1="${y.toFixed(1)}" x2="${plot.left + plot.width}" y2="${y.toFixed(1)}"></line>
        <text class="curve-y-tick" x="${plot.left - 8}" y="${(y + 4).toFixed(1)}">${tick}</text>
      `;
    }).join("");

    const xLabels = xTicks.map((tick) => {
      const x = xFor(tick);
      return `
        <line class="curve-x-tick" x1="${x.toFixed(1)}" y1="${plot.top + plot.height}" x2="${x.toFixed(1)}" y2="${plot.top + plot.height + 4}"></line>
        <text class="curve-x-label" x="${x.toFixed(1)}" y="${plot.top + plot.height + 20}">${tick}k</text>
      `;
    }).join("");

    const baseMarkers = basePoints.map((point) => (
      `<circle class="curve-marker-base" cx="${point.x.toFixed(1)}" cy="${point.y.toFixed(1)}" r="4.1"></circle>`
    )).join("");
    const ourMarkers = ourPoints.map((point) => (
      `<rect class="curve-marker-ours" x="${(point.x - 4).toFixed(1)}" y="${(point.y - 4).toFixed(1)}" width="8" height="8" rx="1.5"></rect>`
    )).join("");
    const yAxisLabel = panelIndex === 0 ? `<text class="curve-axis-label-y" transform="translate(12 96) rotate(-90)">FVD (↓)</text>` : "";

    return `
      <svg class="curve-panel" viewBox="0 0 292 204" aria-label="${panel.title}">
        <title>${panel.title}</title>
        <text class="curve-title fvd-curve-title" x="152" y="19">${panel.title}</text>
        ${grid}
        <line class="curve-axis" x1="${plot.left}" y1="${plot.top + plot.height}" x2="${plot.left + plot.width}" y2="${plot.top + plot.height}"></line>
        <line class="curve-axis" x1="${plot.left}" y1="${plot.top}" x2="${plot.left}" y2="${plot.top + plot.height}"></line>
        ${xLabels}
        ${yAxisLabel}
        <text class="curve-axis-label-x" x="152" y="196">Training Steps</text>
        <path class="curve-gap" d="${fillPath}"></path>
        <path class="curve-line-base" d="${pathFrom(basePoints)}"></path>
        <path class="curve-line-ours" d="${pathFrom(ourPoints)}"></path>
        ${baseMarkers}
        ${ourMarkers}
      </svg>
    `;
  }).join("");

  container.innerHTML = `
    <div class="curve-top-legend" aria-label="FVD curve legend">
      <span><i class="legend-line legend-line-base"></i><i class="legend-dot legend-dot-base"></i>LingBot-VA</span>
      <span><i class="legend-line legend-line-ours"></i><i class="legend-dot legend-dot-ours"></i>Next Forcing (Ours)</span>
    </div>
    <div class="curve-panel-grid">${svgs}</div>
  `;
}

function videoItem(label, file, poster, labelClass = "") {
  return `
    <div class="video-comparison-item">
      <div class="video-comparison-label ${labelClass}">${label}</div>
      <video controls muted autoplay loop playsinline preload="metadata" poster="${poster}">
        <source src="${file}" type="video/mp4">
      </video>
    </div>
  `;
}

function renderCase(item, index) {
  const va = `${item.slug}-lingbot-va`;
  const mcp = `${item.slug}-next-forcing`;
  return `
    <article class="general-case" data-case-index="${index}">
      <div class="video-comparison">
        ${videoItem("LingBot-VA", `assets/videos/general/${va}.mp4`, `assets/posters/${va}.jpg`)}
        ${videoItem("Next Forcing", `assets/videos/general/${mcp}.mp4`, `assets/posters/${mcp}.jpg`, "ours-label")}
      </div>
      <p class="prompt-text">${escapeHtml(item.prompt)}</p>
    </article>
  `;
}

function syncCaseVideos(card) {
  const videos = Array.from(card.querySelectorAll("video"));
  if (videos.length < 2) return;

  videos.forEach((video) => {
    video.muted = true;
    video.play().catch(() => {});
  });

  const [leader, follower] = videos;
  const resync = () => {
    if (Math.abs(leader.currentTime - follower.currentTime) > 0.15) {
      follower.currentTime = leader.currentTime;
    }
  };

  leader.addEventListener("timeupdate", resync);
  leader.addEventListener("play", () => follower.play().catch(() => {}));
  leader.addEventListener("pause", () => follower.pause());
}

function initGeneralComparison() {
  const list = document.querySelector("#general-comparison-list");
  if (!list) return;
  list.innerHTML = cases.map(renderCase).join("");
  list.querySelectorAll(".general-case").forEach(syncCaseVideos);
}

function initRealWorldDemos() {
  const video = document.querySelector("#realworld-demo-video");
  const description = document.querySelector("#realworld-task-description");
  const tabs = Array.from(document.querySelectorAll(".realworld-tab"));
  if (!video || tabs.length === 0) return;

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      if (tab.classList.contains("active")) return;

      tabs.forEach((item) => {
        item.classList.remove("active");
        item.setAttribute("aria-selected", "false");
      });
      tab.classList.add("active");
      tab.setAttribute("aria-selected", "true");

      const source = video.querySelector("source");
      if (source && tab.dataset.videoSrc) source.src = tab.dataset.videoSrc;
      if (tab.dataset.videoPoster) video.poster = tab.dataset.videoPoster;
      if (description && tab.dataset.demoDescription) description.textContent = tab.dataset.demoDescription;

      video.load();
      video.muted = true;
      video.play().catch(() => {});
    });
  });
}

function initRoboTwinCarousel() {
  const carousel = document.querySelector("#robotwin-carousel");
  const mainVideo = document.querySelector("#robotwin-main-video");
  const title = document.querySelector("#robotwin-main-title");
  if (!carousel || !mainVideo) return;

  const thumbs = Array.from(carousel.querySelectorAll(".sidebar-thumb"));
  thumbs.forEach((thumb) => {
    thumb.addEventListener("click", () => {
      if (thumb.classList.contains("active")) return;

      thumbs.forEach((item) => item.classList.remove("active"));
      thumb.classList.add("active");

      const source = mainVideo.querySelector("source");
      const videoSrc = thumb.dataset.videoSrc;
      if (source && videoSrc) source.src = videoSrc;
      if (thumb.dataset.videoPoster) mainVideo.poster = thumb.dataset.videoPoster;
      if (title && thumb.dataset.mainTitle) title.textContent = thumb.dataset.mainTitle;

      mainVideo.load();
      mainVideo.muted = true;
      mainVideo.play().catch(() => {});
    });
  });
}

renderRobotwinCurveChart();
renderFvdCurveChart();
initRealWorldDemos();
initRoboTwinCarousel();
initGeneralComparison();
