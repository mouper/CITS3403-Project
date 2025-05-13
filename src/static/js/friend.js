document.querySelectorAll('.clickable-friend').forEach(el => {
  el.addEventListener('click', () => {
    const username = el.dataset.username;
    fetch(`/user_preview/${username}`)
      .then(res => res.text())
      .then(html => {
        document.getElementById('friendPreviewContainer').innerHTML = html;
        document.getElementById('friendModal').style.display = 'block';
      });
  });
});
