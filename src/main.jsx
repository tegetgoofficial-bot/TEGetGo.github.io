// HMR Test
import React, { useState, useEffect, createContext } from 'react';
import ReactDOM from 'react-dom/client';
import ReactDOMServer from 'react-dom/server';


// ----------------------
// Global Variables
// ----------------------


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
              key={item.item_id}
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
        const onClickLogic = `event.preventDefault(); window.dispatchCategorySelect('${cat.category_id}')`;
        const linkHtml = ReactDOMServer.renderToString(
          <CategoryLink 
            id={cat.category_id} 
            // FIX: Use itemType if Category_Name is missing
            name={cat.item_type} 
          />
        );

        // Change 'const' to 'let' so you can overwrite it with the stringified version later
        let itemProps = ({
          id: cat.category_id,
          name: cat.item_type, 
          type: cat.item_type,
          link: linkHtml,
          linkLogic: onClickLogic,
          reactType: "react-loop-wrapper",
          others: {}
        });

        // This loop is now correct for a dictionary
        for (let key in cat) {
          if (key !== "category_id" && key !== "item_type") {
            itemProps.others[key] = cat[key];
          }
        }

        // Now this reassignment will work instead of crashing
        itemProps = JSON.stringify(itemProps); 

        return (
          <JinjaBlock 
            key={cat.category_id}
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
  // Add this safety check at the very top
  if (!el || !(el instanceof HTMLElement)) return; 
  
  if (el.getAttribute('data-react-claimed') === 'true') return;

  const { folder, file, component, props: propsRaw } = el.dataset;
  
  try {
  let props = propsRaw ? JSON.parse(propsRaw) : {};
  
  // 1. Check if the incoming data is wrapped in a "props" key
  // This handles your <div data-props='{"props": { ... }}'>
  const actualData = props.props ? props.props : props;

  if (!el._reactRoot) {
    el._reactRoot = ReactDOM.createRoot(el);
  }
  el.setAttribute('data-react-claimed', 'true');

  // 2. Check the DICTIONARY_MAP using the top-level keys
  const key = Object.keys(props)[0];
  
  if (DICTIONARY_MAP[key]) {
    const ActiveComponent = DICTIONARY_MAP[key];
    el._reactRoot.render(<ActiveComponent {...props} folder={folder} file={file} block={component} />);
  } else {
    // 3. Pass the "unwrapped" data to the JinjaBlock so Flask sees it clearly
    const cleanProps = JSON.stringify(actualData);
    el._reactRoot.render(<JinjaBlock folder={folder} file={file} block={component} props={cleanProps} />);
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
  // Check if it exists FIRST
  if (!searchInput) return; 

  searchInput.addEventListener('input', () => {
    const searchValue = searchInput.value.toLowerCase().trim();
    // Re-select cards inside the function
    const cards = document.querySelectorAll('.card'); 

    cards.forEach(card => {
      const nameEl = card.querySelector('.card-name');
      const name = nameEl ? nameEl.textContent.toLowerCase() : "";
      const categories = (card.dataset.category || '').toLowerCase();
      const categoryList = categories.split(',').map(c => c.trim());

      const matchesName = name.includes(searchValue);
      const matchesCategory = categoryList.some(c => c.includes(searchValue));

      card.style.display = (matchesName || matchesCategory) ? 'block' : 'none';
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

// Updated Line 332
const rootElement = document.getElementById('root');

if (rootElement) {
    const root = ReactDOM.createRoot(rootElement);
    root.render(<App />);
} else {
    // If there's no #root, we just skip it so the rest of the script (slider) works
    console.warn("Element #root not found. Skipping main React mount.");
}

// Keep your search init here
window.addEventListener('load', () => {
    initSearch();
});


window.moveSlide = function(button, step) {
    // 1. Find the local elements for THIS specific slider
    const wrapper = button.closest('.slideshow-wrapper');
    const viewport = wrapper.querySelector('.slideshow-viewport');
    const slides = viewport.querySelectorAll('.slide-item');
    
    // 2. Get or Initialize this slider's unique state
    // We store the index/moving state directly on the element so they don't mix up
    if (viewport.dataset.isMoving === "true") return;
    let currentIndex = parseInt(viewport.dataset.index) || 1;

    // 3. Update the state
    viewport.dataset.isMoving = "true";
    currentIndex += step;
    viewport.dataset.index = currentIndex;

    // 4. Perform the Move
    viewport.style.transition = "transform 0.5s cubic-bezier(0.23, 1, 0.32, 1)";
    viewport.style.transform = `translateX(${-currentIndex * 100}%)`;

    // 5. The Flexible Teleport
    const teleport = () => {
        viewport.style.transition = "none";
        
        const totalSlides = slides.length;
        let newIndex = currentIndex;

        if (currentIndex >= totalSlides - 1) {
            newIndex = 1;
        } else if (currentIndex <= 0) {
            newIndex = totalSlides - 2;
        }

        if (newIndex !== currentIndex) {
            currentIndex = newIndex;
            viewport.dataset.index = currentIndex;
            void viewport.offsetWidth; // Force Reflow
            viewport.style.transform = `translateX(${-currentIndex * 100}%)`;
        }

        viewport.dataset.isMoving = "false";
        viewport.removeEventListener('transitionend', teleport);
    };

    viewport.addEventListener('transitionend', teleport, { once: true });
};