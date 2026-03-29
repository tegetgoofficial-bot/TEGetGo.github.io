// HMR Test
import React, { useState, useEffect, createContext } from 'react';
import ReactDOM from 'react-dom/client';

// ----------------------
// JinjaBlock Component
// ----------------------
const JinjaBlock = ({ folder, file, block, props }) => {
  const [html, setHtml] = useState('');

  useEffect(() => {
    // Ensure props is at least "{}" before encoding
    const safeProps = props && props !== 'undefined' ? props : '{}';
    const url = `/component/${folder}/${file}/${block}?props=${encodeURIComponent(safeProps)}`;
    
    fetch(url)
      .then(res => res.text())
      .then(data => setHtml(data));
  }, [folder, file, block, props]);

  return <div dangerouslySetInnerHTML={{ __html: html }} />;
};



// ----------------------
// Email Copy Logic
// ----------------------
function copyEmail() {
  navigator.clipboard.writeText('tegetgoofficial@gmail.com');
  document.getElementById('copy-msg').style.display = 'block';
  setTimeout(() => {
    document.getElementById('copy-msg').style.display = 'none';
  }, 2000);
}

const observer = new MutationObserver(() => {
  document.querySelectorAll(".contact-email").forEach(el => {
    el.onclick = copyEmail;
  });
});

observer.observe(document.body, { childList: true, subtree: true });

if (import.meta.env.DEV) {
  import('../app/statics/css/style.css');
}

// ----------------------
// Mount Function
// ----------------------
function mountJinjaBlock(el) {
  const { folder, file, component, props: propsRaw } = el.dataset;
  const props = propsRaw ? JSON.parse(propsRaw) : {};
  const root = ReactDOM.createRoot(el);

  if (component === "CategoryButtonGroups") {
    root.render(<CategoryButtonGroups categories={props.categories} />);
  } 
  else if (component === "CategoryLink") {
    // Keep your single link logic too just in case
    root.render(<CategoryLink {...props} onSelect={(id) => window.dispatchCategorySelect(id)} />);
  }
  else if (folder && file) {
    root.render(<JinjaBlock folder={folder} file={file} block={component} props={propsRaw} />);
  }
}


// ----------------------
// Category Overlay Component
// ----------------------

const CategoryLink = ({ id, name, onSelect }) => {
  const handleClick = (e) => {
    e.preventDefault(); // Stop the page from reloading/404ing
    onSelect(id);       // Tell the parent to show the Overlay
  };

  return <a href={`/category/${id}`} onClick={handleClick}>{name}</a>;
};


const CategoryOverlay = ({ data, onClose }) => {
  return (
    <div className="modal-overlay">
      <div className="modal-content">
        {/* OPTION A: Header shows the specific category clicked */}
        <div className="modal-header">
           <h2>Results for {data.category_name}</h2>
           <button onClick={onClose}>✕</button>
        </div>

        <div className="cards-grid">
          {data.items.map(item => (
            <div className="pop-card" key={item.Item_ID}>
              {/* NEW: Image Wrapper for consistent sizing */}
              <div className="pop-card-img-wrap">
                <img src={item.image} alt={item.name} />
              </div>

              <h3>{item.name}</h3>
              
              <div className="tag-container">
                {item.all_tags.split(', ').map(tag => (
                  <span key={tag} className="tag-pill">{tag}</span>
                ))}
              </div>

              <p className="price">${item.cost}</p>
              <a href={`/go/${item.Item_ID}`} className="btn">Check it out</a>
            </div>
          ))}

        </div>
      </div>
    </div>
  );
};

const CategoryButtonGroups = ({ categories }) => {
  return (
    <div className="flex-wrapper"> 
      {categories.map(cat => (
        <div key={cat.Category_ID} className="item-wrap">
          <CategoryLink 
            id={cat.Category_ID} 
            name={cat.itemType} 
            onSelect={(id) => window.dispatchCategorySelect(id)} 
          />
        </div>
      ))}
    </div>
  );
};


const handleCategorySelect = (id) => {
  setLoading(true); // START LOADING
  document.getElementById('main-content').classList.add('blur-bg');
  
  fetch(`/api/category/${id}`)
    .then(res => res.json())
    .then(data => {
      setSelectedData(data);
      setLoading(false); // STOP LOADING
    })
    .catch(() => {
      setLoading(false);
      document.getElementById('main-content').classList.remove('blur-bg');
    });
};


const App = () => {
  const [selectedData, setSelectedData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // This connects your CategoryLink components to this App's state
    window.dispatchCategorySelect = (id) => {
      handleCategorySelect(id);
    };
  }, []);

  const handleCategorySelect = (id) => {
    setLoading(true); // Show the "Fetching..." spinner
    document.getElementById('main-content').classList.add('blur-bg');
    
    fetch(`/api/category/${id}`)
      .then(res => res.json())
      .then(data => {
        setSelectedData(data);
        setLoading(false); // Hide spinner
      })
      .catch((err) => {
        console.error("Fetch error:", err);
        setLoading(false);
        document.getElementById('main-content').classList.remove('blur-bg');
      });
  };

  const closeOverlay = () => {
    setSelectedData(null);
    document.getElementById('main-content').classList.remove('blur-bg');
  };

  return (
    <>
      {selectedData && (
        <CategoryOverlay data={selectedData} onClose={closeOverlay} />
      )}
      
      {loading && (
        <div className="loading-spinner-overlay">
            <div className="spinner">Fetching Picks...</div>
        </div>
      )}
    </>
  );
};


// ----------------------
// Initialization
// ----------------------

// 1. Mount the App (The Overlay Manager)
const overlayRoot = document.getElementById('overlay-root');
if (overlayRoot) {
  const root = ReactDOM.createRoot(overlayRoot);
  // We need a way to trigger the App's state from the outside 
  // (from the Jinja-rendered links).
  window.showCategory = (id) => {
     // This is a bridge to trigger the React state from vanilla JS links
  };
  root.render(<App />);
}

// ----------------------
// Auto-Scanner
// ----------------------
document.querySelectorAll('.react-target').forEach(mountJinjaBlock);