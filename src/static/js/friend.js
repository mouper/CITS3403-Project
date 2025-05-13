function ensureFriendPreviewStylesLoaded() {
  const styles = [
    "/static/css/account.css",
    "/static/css/typography.css",
    "/static/css/colours.css"
  ];
  styles.forEach(href => {
    if (!document.querySelector(`link[href="${href}"]`)) {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = href;
      document.head.appendChild(link);
    }
  });
}

document.querySelectorAll('.clickable-friend').forEach(el => {
  el.addEventListener('click', () => {
    const username = el.dataset.username;
    fetch(`/user_preview/${username}`)
      .then(res => res.text())
      .then(html => {
        ensureFriendPreviewStylesLoaded(); // ✅ 插入所需 CSS
        document.getElementById('friendPreviewContainer').innerHTML = html;
        document.getElementById('friendModal').style.display = 'block';
      });
  });
});
