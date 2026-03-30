// HMR Test
import React, { useState, useEffect, createContext } from 'react';
import ReactDOM from 'react-dom/client';
import ReactDOMServer from 'react-dom/server';


// ----------------------
// Helper Functions
// ----------------------
const isDictionary = (val) => {
  return val != null && typeof val === 'object' && !Array.isArray(val);
};

// ----------------------
// Category Overlay Component
// ----------------------

// This makes a link
const CategoryLink = ({ id, name }) => {
  // Use data-on-click so React doesn't strip it during renderToString
  return (
    <a 
      href={`/category/${id}`} 
      data-on-click={`event.preventDefault(); window.dispatchCategorySelect('${id}')`}
      className="category-link"
    >
      {name}
    </a>
  );
};



const CategoryOverlay = ({ data, onClose }) => {
  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
           <h2>Results for {data.category_name}</h2>
           <button onClick={onClose}>✕</button>
        </div>

        <div className="cards-grid">
          {data.items.map(item => (
            /* 
               Instead of hardcoding the card here, 
               let the JinjaBlock handle the "Skin" and the tags 
            */
            <JinjaBlock 
              key={item.Item_ID}
              folder="assets" 
              file="card" 
              block="popup_card" 
              // Safety: Ensure all_tags exists so the split doesn't fail
              props={JSON.stringify({ ...item, all_tags: item.all_tags || "" })} 
            />
          ))}
        </div>
      </div>
    </div>
  );
};



const CategoryButtonGroups = ({ categories, folder, file, block }) => {
  return (
    <div className="react-loop-wrapper">
      {categories.map((cat) => {
        const linkHtml = ReactDOMServer.renderToString(
          <CategoryLink 
            id={cat.Category_ID} 
            // FIX: Use itemType if Category_Name is missing
            name={cat.itemType} 
          />
        );

        const itemProps = JSON.stringify({
          id: cat.Category_ID,
          name: cat.itemType, // Match what your Jinja {{ props.name }} expects
          type: cat.itemType,
          link: linkHtml
        });

        return (
          <JinjaBlock 
            key={cat.Category_ID}
            folder={folder} 
            file={file} 
            block={block} 
            props={itemProps} 
          />
        );
      })}
    </div>
  );
};



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
const DICTIONARY_MAP = {
  categories: CategoryButtonGroups, // This matches the 'categories' key in your HTML data-props
};


// Add this above the mountJinjaBlock function
const rootCache = new Map();

function mountJinjaBlock(el) {
  const { folder, file, component, props: propsRaw } = el.dataset;
  let props = {};
  
  try {
    props = propsRaw ? JSON.parse(propsRaw) : {};
  } catch (e) {
    console.error("Failed to parse props", e);
  }

  // 1. Correct Root Management
  let root = rootCache.get(el);
  if (!root) {
    root = ReactDOM.createRoot(el);
    rootCache.set(el, root);
  }

  // 2. Identify the Data Key
  if (isDictionary(props)) {
    const keys = Object.keys(props);
    const keyToMatch = keys[0]; // e.g., "categories"

    // 3. Match against your DICTIONARY_MAP
    if (DICTIONARY_MAP.hasOwnProperty(keyToMatch)) {
      const ActiveComponent = DICTIONARY_MAP[keyToMatch];
      root.render(
        <ActiveComponent 
          {...props} 
          folder={folder} 
          file={file} 
          block={component} 
        />
      );
      return; 
    }
  } 
  
  // Fallback for standard blocks
  if (folder && file && component) {
    root.render(<JinjaBlock folder={folder} file={file} block={component} props={propsRaw} />);
  }
}



const App = () => {
  const [selectedData, setSelectedData] = useState(null);
  const [loading, setLoading] = useState(false);

  // MOVE THIS INSIDE THE COMPONENT
  const handleCategorySelect = (id) => {
    setLoading(true);
    document.getElementById('main-content')?.classList.add('blur-bg');
    
    fetch(`/api/category/${id}`)
      .then(res => res.json())
      .then(data => {
        setSelectedData(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Fetch error:", err);
        setLoading(false);
        document.getElementById('main-content')?.classList.remove('blur-bg');
      });
  };

  useEffect(() => {
    // This now correctly calls the internal handleCategorySelect
    window.dispatchCategorySelect = (id) => {
      handleCategorySelect(id);
    };

    if (selectedData) {
      setTimeout(() => {
        document.querySelectorAll('.react-target').forEach(mountJinjaBlock);
      }, 10);
    }
  }, [selectedData])

  const closeOverlay = () => {
    setSelectedData(null);
    document.getElementById('main-content')?.classList.remove('blur-bg');
  };

  return (
    <>
      {selectedData && <CategoryOverlay data={selectedData} onClose={closeOverlay} />}
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
// AT THE VERY BOTTOM OF main.jsx
if (!window.__SCANNER_INIT__) {
  window.__SCANNER_INIT__ = true;
  document.querySelectorAll('.react-target').forEach(mountJinjaBlock);
}
