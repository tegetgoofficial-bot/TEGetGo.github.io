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
      className="card-link"
    >
     View picks →
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
    <>
      {categories.map((cat) => {
        const onClickLogic = `event.preventDefault(); window.dispatchCategorySelect('${cat.Category_ID}')`;
        const linkHtml = ReactDOMServer.renderToString(
          <CategoryLink 
            id={cat.Category_ID} 
            // FIX: Use itemType if Category_Name is missing
            name={cat.itemType} 
          />
        );

        // Change 'const' to 'let' so you can overwrite it with the stringified version later
        let itemProps = ({
          id: cat.Category_ID,
          name: cat.itemType, 
          type: cat.itemType,
          link: linkHtml,
          linkLogic: onClickLogic,
          reactType: "react-loop-wrapper",
          others: {}
        });

        // This loop is now correct for a dictionary
        for (let key in cat) {
          if (key !== "Category_ID" && key !== "itemType") {
            itemProps.others[key] = cat[key];
          }
        }

        // Now this reassignment will work instead of crashing
        itemProps = JSON.stringify(itemProps); 

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
    </>
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


function mountJinjaBlock(el) {
  if (el.getAttribute('data-react-claimed') === 'true') return;

  const { folder, file, component, props: propsRaw } = el.dataset;
  
  try {
    // If propsRaw is empty or missing, it will check the API data instead
    let props = propsRaw ? JSON.parse(propsRaw) : {};
    
    // If the component is 'teste' and props are empty, don't mount yet
    if (component === 'teste' && (!props.categories || props.categories.length === 0)) {
       return; 
    }

    if (!el._reactRoot) {
      el._reactRoot = ReactDOM.createRoot(el);
    }
    el.setAttribute('data-react-claimed', 'true');

    const key = Object.keys(props)[0];
    if (DICTIONARY_MAP[key]) {
      const ActiveComponent = DICTIONARY_MAP[key];
      el._reactRoot.render(<ActiveComponent {...props} folder={folder} file={file} block={component} />);
    } else {
      el._reactRoot.render(<JinjaBlock folder={folder} file={file} block={component} props={propsRaw} />);
    }
  } catch (e) {
    console.error("Mount failed:", e);
  }
}



const App = () => {
  const [selectedData, setSelectedData] = useState(null);
  const [loading, setLoading] = useState(false);
  
  // NEW: Store the categories from the API
  const [initialData, setInitialData] = useState({ categories: [] });

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

  // NEW: This effect handles the initial data load ONCE
  useEffect(() => {
    window.dispatchCategorySelect = (id) => handleCategorySelect(id);

    fetch('/api/initial-data')
      .then(res => res.json())
      .then(json => {
        setInitialData(json);
        // Once data arrives, tell the scanner to check for the 'teste' section
        window.dispatchEvent(new Event('initialDataReady'));
      })
      .catch(err => console.error("API Error:", err));
  }, []); // Empty array = run once on load

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
// Search Input Logic
// ----------------------
function initSearch() {
  const searchInput = document.querySelector('#searchInput');
  // Re-select cards inside the function so it finds the ones React just made
  const cards = document.querySelectorAll('.card'); 

  searchInput.addEventListener('input', () => {
    const searchValue = searchInput.value.toLowerCase().trim();

    cards.forEach(card => {
      const name = card.querySelector('.card-name').textContent.toLowerCase();
      const categories = (card.dataset.category || '').toLowerCase();

      const categoryList = categories ? categories.split(',').map(c => c.trim()) : [];


      const matchesName = name.includes(searchValue);
      const matchesCategory = categoryList.some(c => c.includes(searchValue));
      

      if (matchesName || matchesCategory) {
        card.style.display = 'block';
      } else {
        card.style.display = 'none';
      }
    });
  });
}

// ----------------------
// Auto-Scanner
// ----------------------
// AT THE VERY BOTTOM OF main.jsx
if (!window.__ACTIVE_SCANNER__) {
  window.__ACTIVE_SCANNER__ = true;
  
  const run = () => {
    document.querySelectorAll('.react-target').forEach(mountJinjaBlock);
  };

  // Run on load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }

  // NEW: Run again when the API data arrives
  window.addEventListener('initialDataReady', run);
}

// ----------------------
// After Auto-Scanner
// ----------------------

window.addEventListener('DOMContentLoaded', () => {
  setTimeout(initSearch, 500); // Give React 500ms to "paint" the cards
});
