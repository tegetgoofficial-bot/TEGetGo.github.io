// HMR Test 
import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';


// src/main.jsx
const JinjaBlock = ({ folder, file, block }) => {
  const [html, setHtml] = useState('');

  useEffect(() => {
    // Hits the path: /component/layouts/content/nav
    fetch(`/component/${folder}/${file}/${block}`)
      .then(res => res.text())
      .then(data => setHtml(data));
  }, [folder, file, block]);

  return <div dangerouslySetInnerHTML={{ __html: html }} />;
};

const contactEmail = document.querySelectorAll(".contact-email");

function copyEmail() {
  navigator.clipboard.writeText('tegetgoofficial@gmail.com');
  document.getElementById('copy-msg').style.display = 'block';
  setTimeout(() => {
    document.getElementById('copy-msg').style.display = 'none';
  }, 2000);
}

contactEmail.forEach(email => {
  email.addEventListener('click', () => {
    copyEmail();
  });
});


if (import.meta.env.DEV) {
  import('../app/statics/css/style.css');
}

// Auto-Scanner
document.querySelectorAll('.react-target').forEach(el => {
  const folder = el.getAttribute('data-folder');    // e.g. "layouts"
  const file   = el.getAttribute('data-file');      // e.g. "content"
  const block  = el.getAttribute('data-component'); // e.g. "nav"
  
  ReactDOM.createRoot(el).render(
    <JinjaBlock folder={folder} file={file} block={block} />
  );
});
