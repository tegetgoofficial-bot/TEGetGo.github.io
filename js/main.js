function copyEmail() {
  navigator.clipboard.writeText('TEGetGoOfficial@gmail.com');
  document.getElementById('copy-msg').style.display = 'block';
  setTimeout(() => {
    document.getElementById('copy-msg').style.display = 'none';
  }, 2000);
}
