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

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
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

initGeneralComparison();
