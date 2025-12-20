document.querySelectorAll(".interaction-buttons").forEach((section) => {
    
    const likeBtn = section.querySelector(".likeBtn");
    const favBtn = section.querySelector(".favBtn");
    const playlistBtn = section.querySelector(".playlistBtn");
    const commentBtn = section.querySelector(".commentBtn");

    // LIKE
    likeBtn.addEventListener("click", () => {
        likeBtn.classList.toggle("liked");
        likeBtn.textContent = 
            likeBtn.classList.contains("liked") ? "Liked ❤️" : "Like ❤️";
    });

    // FAVORITE
    favBtn.addEventListener("click", () => {
        favBtn.classList.toggle("favorited");
        favBtn.textContent = 
            favBtn.classList.contains("favorited") ? "Favorited ⭐" : "Add to Favorites ⭐";
    });

    // PLAYLIST
    playlistBtn.addEventListener("click", () => {
        let name = prompt("Enter playlist name:");
        if (name) alert(`Added to playlist: ${name}`);
    });

    // COMMENT
    commentBtn.addEventListener("click", () => {
        let comment = prompt("Write your comment:");
        if (comment) alert(`Comment added: ${comment}`);
    });
});
const messages = [
    "🔥 Amazing work! Truly impressive!",
    "💪 Keep going… you're leveling up every day!",
    "🚀 Outstanding performance! Your passion really shows!",
    "🏆 Great achievement! You should be proud!",
    "📚 Your mind is growing stronger—keep it up!",
    "✨ Excellent progress! You're doing fantastic!",
    "🌟 You're crushing it! Keep pushing forward!",
    "🔥 You’re on fire! Amazing dedication!",
    "💥 Brilliant effort! You're unstoppable!",
    "🌈 Keep shining, you're doing amazing!"
];

// ع
const allCardsLinks = document.querySelectorAll(
    " .movie-card a"
);

allCardsLinks.forEach(link => {
    link.addEventListener("click", function (event) {
        event.preventDefault();

        const title =
            this.querySelector("h3")?.innerText ||
            this.parentElement?.querySelector("h3")?.innerText ||
            "This Item";

        const randomMsg = messages[Math.floor(Math.random() * messages.length)];

        const msgBox = document.createElement("div");
        msgBox.className = "positive-msg";

        msgBox.innerHTML = `🎉 You opened: <b>${title}</b><br>${randomMsg}`;
        document.body.appendChild(msgBox);

        // الرسالة تقعد 12 ثانية
        setTimeout(() => msgBox.remove(), 12000);

        // تأخير فتح الصفحة
        setTimeout(() => {
            window.location.href = this.href;
        }, 3500);
    });
});
