fetch("http://localhost:5000/rss")
  .then(response => response.text())
  .then(data => {
    const parser = new DOMParser();
    const xml = parser.parseFromString(data, "application/xml");
    const items = xml.querySelectorAll("item");

    let html = "";
    items.forEach(item => {
      const title = item.querySelector("title").textContent;
      const link = item.querySelector("link").textContent;
      const description = item.querySelector("description").textContent;

      html += `
        <div class="item">
          <h3><a href="${link}" target="_blank">${title}</a></h3>
          <p>${description}</p>
        </div>
      `;
    });

    document.getElementById("rss-feed").innerHTML = html;
  });
