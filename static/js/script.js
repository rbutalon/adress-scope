const state = { data: null, map: null, marker: null };
const $ = (id) => document.getElementById(id);
const readable = (value) => value === null || value === undefined || value === "" ? "Unavailable" : value;

const MAP_TILE_URL = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
const MAP_ATTRIBUTION = '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">OpenStreetMap</a> contributors';

function setAddress(version, entry) {
  const address = $(`${version}-address`);
  const status = $(`${version}-status`);
  const detail = $(`${version}-detail`);
  address.textContent = entry.available ? entry.address : "Unavailable";
  address.classList.toggle("has-value", entry.available);
  status.textContent = entry.available ? "Available" : "Unavailable";
  status.className = `status ${entry.available ? "available" : "unavailable"}`;
  detail.textContent = entry.available ? "Public address detected" : `No ${version.toUpperCase()} connectivity detected`;
}

function safeNumber(value) {
  if (value === null || value === undefined || value === "") return null;
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function readCoordinates(location) {
  if (!location) return null;
  const lat = safeNumber(location.latitude);
  const lon = safeNumber(location.longitude);
  if (lat === null || lon === null || Math.abs(lat) > 90 || Math.abs(lon) > 180) return null;
  return { lat, lon };
}

function popupContent(location) {
  const wrapper = document.createElement("div");
  const title = document.createElement("strong");
  const subtitle = document.createElement("div");
  const parts = [location.city, location.region, location.country].filter(Boolean);
  title.textContent = parts.length ? parts.join(", ") : "Approximate IP location";
  subtitle.textContent = "Approximate location from the IP database.";
  wrapper.append(title, subtitle);
  return wrapper;
}

function ensureMap() {
  if (state.map) return true;
  if (typeof L === "undefined") return false;
  state.map = L.map("map", { scrollWheelZoom: false });
  L.tileLayer(MAP_TILE_URL, { maxZoom: 19, attribution: MAP_ATTRIBUTION }).addTo(state.map);
  state.marker = L.circleMarker([0, 0], {
    radius: 9,
    color: "#102c3b",
    weight: 2,
    fillColor: "#38c3ca",
    fillOpacity: 1,
  }).addTo(state.map);
  return true;
}

function renderMap(location) {
  const coords = readCoordinates(location);
  const mapNode = $("map");
  const emptyNode = $("map-empty");
  const coordsLabel = $("map-coords");
  const emptyText = $("map-empty-text");
  const osmLink = $("map-osm-link");
  const googleLink = $("map-google-link");

  if (!coords) {
    mapNode.hidden = true;
    emptyNode.hidden = false;
    emptyText.textContent = "No coordinates yet. Run a scan to plot the approximate public location.";
    coordsLabel.textContent = "Location unavailable";
    osmLink.removeAttribute("href");
    googleLink.removeAttribute("href");
    return;
  }

  coordsLabel.textContent = `${coords.lat.toFixed(4)}, ${coords.lon.toFixed(4)}`;
  osmLink.href = `https://www.openstreetmap.org/?mlat=${coords.lat}&mlon=${coords.lon}#map=12/${coords.lat}/${coords.lon}`;
  googleLink.href = `https://www.google.com/maps/search/?api=1&query=${coords.lat},${coords.lon}`;

  mapNode.hidden = false;
  emptyNode.hidden = true;
  if (!ensureMap()) {
    mapNode.hidden = true;
    emptyNode.hidden = false;
    emptyText.textContent = "The interactive map library could not load. Use the map links below.";
    coordsLabel.textContent = "Map unavailable";
    return;
  }

  state.marker.setLatLng([coords.lat, coords.lon]);
  state.marker.bindPopup(popupContent(location));
  state.map.setView([coords.lat, coords.lon], 10);
  state.map.invalidateSize();
}

function renderUpdated(checkedAt) {
  const label = $("last-updated");
  const stamp = checkedAt ? new Date(checkedAt) : null;
  if (!stamp || Number.isNaN(stamp.getTime())) {
    label.textContent = "Updated just now";
    return;
  }
  label.textContent = `Updated ${stamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
}

function render(data) {
  state.data = data;
  const unavailable = { available: false, address: null };
  setAddress("ipv4", data.ipv4 || unavailable);
  setAddress("ipv6", data.ipv6 || unavailable);
  Object.entries(data.location || {}).forEach(([key, value]) => {
    const node = $(key);
    if (node) node.textContent = readable(value);
  });
  Object.entries(data.network || {}).forEach(([key, value]) => {
    const node = $(key);
    if (node) node.textContent = readable(value);
  });
  renderMap(data.location);
  renderUpdated(data.checked_at);
  $("refresh-button").disabled = false;
  const warnings = (data.warnings || []).map((warning) => warning.message);
  if (!data.success) showNotice(data.message || "Could not retrieve IP information.");
  else if (warnings.length) showNotice(`Some information could not be loaded: ${[...new Set(warnings)].join(" ")}`);
  else { $("notice").hidden = true; }
}

function showNotice(message) { $("notice").textContent = message; $("notice").hidden = false; }

async function loadInfo() {
  $("loading").hidden = false;
  $("check-button").disabled = true;
  $("refresh-button").disabled = true;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch("/api/ip-info", { headers: { Accept: "application/json" }, signal: controller.signal });
    const data = await response.json();
    render(data);
  } catch (error) {
    const message = error.name === "AbortError"
      ? "The lookup timed out. Check your connection and try again."
      : "The dashboard could not reach its Flask backend. Check that the server is running.";
    showNotice(message);
  } finally {
    clearTimeout(timer);
    $("loading").hidden = true;
    $("check-button").disabled = false;
  }
}

async function copyAddress(version, button) {
  const entry = state.data && state.data[version];
  if (!entry || !entry.available) { showNotice(`There is no available ${version.toUpperCase()} address to copy.`); return; }
  try {
    await navigator.clipboard.writeText(entry.address);
    button.innerHTML = "Copied <span>✓</span>";
    setTimeout(() => { button.innerHTML = "Copy <span>□</span>"; }, 1400);
  } catch (error) { showNotice("Clipboard access is unavailable in this browser."); }
}

$("check-button").addEventListener("click", loadInfo);
$("refresh-button").addEventListener("click", loadInfo);
document.querySelectorAll(".copy-button").forEach((button) => button.addEventListener("click", () => copyAddress(button.dataset.copy, button)));
