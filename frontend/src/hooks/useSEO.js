import { useEffect } from 'react';

export function useSEO({ title, description, url, image, schema }) {
  useEffect(() => {
    if (title) document.title = title;
    
    const setMeta = (name, content, property = false) => {
      if (!content) return;
      const attr = property ? 'property' : 'name';
      let el = document.querySelector(`meta[${attr}="${name}"]`);
      if (!el) {
        el = document.createElement('meta');
        el.setAttribute(attr, name);
        document.head.appendChild(el);
      }
      el.setAttribute('content', content);
    };

    setMeta('description', description);
    setMeta('og:title', title, true);
    setMeta('og:description', description, true);
    if (url) setMeta('og:url', url, true);
    if (image) setMeta('og:image', image, true);
    setMeta('twitter:title', title, true);
    setMeta('twitter:description', description, true);
    if (image) setMeta('twitter:image', image, true);

    let schemaScript = null;
    if (schema) {
      schemaScript = document.createElement('script');
      schemaScript.type = 'application/ld+json';
      schemaScript.innerText = JSON.stringify(schema);
      document.head.appendChild(schemaScript);
    }

    return () => {
      if (schemaScript && document.head.contains(schemaScript)) {
        document.head.removeChild(schemaScript);
      }
    };
  }, [title, description, url, image, schema]);
}
