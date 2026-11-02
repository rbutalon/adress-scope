const state = { data: null };
const $ = (id) => document.getElementById(id);
const readable = (value) => value === null || value === undefined || value === "" ? "Unavailable" : value;

function setAddress(version, entry) {
  const address = $(`${version}-address`);
  const status = $(`${version}-status`);
  const detail = $(`${version}-detail`);
  address.textContent = entry.available ? entry.address : "Unavailable";
  address.classList.toggle("has-value", entry.available);
  status.textContent = entry.available ? "Available" : "Unavailable";
  status.className = `status ${entry.available ? "available" : "unavailable"}`;
  detail.textContent = entry.available ? "Public address detected" : "No ${version.toUpperCase()} connectivity detected";
}

function render(data) {
  state.data = data;
  setAddress("ipv4", data.ipv4);
  setAddress("ipv6", data.ipv6);
  Object.entries(data.location).forEach(([key, value]) => { $(key).textContent = readable(value); });
  Object.entries(data.network).forEach(([key, value]) => { $(key).textContent = readable(value); });
  $("refresh-button").disabled = false;
  const warnings = (data.warnings || []).map((warning) => warning.message);
  if (!data.success) showNotice(data.message || "Could not retrieve IP information.");
  else if (warnings.length) showNotice(`Some information could not be loaded: ${[...new Set(warnings)].join(" ")}`);
  else { $("notice").hidden = true; }
}

function showNotice(message) { $("notice").textContent = message; $("notice").hidden = false; }

async function loadInfo() {
  $("loading").hidden = false; $("check-button").disabled = true; $("refresh-button").disabled = true;
  try { const response = await fetch("/api/ip-info", { headers: { Accept: "application/json" } }); const data = await response.json(); render(data); }
  catch (error) { showNotice("The dashboard could not reach its Flask backend. Check that the server is running."); }
  finally { $("loading").hidden = true; $("check-button").disabled = false; }
}

async function copyAddress(version, button) {
  const entry = state.data && state.data[version];
  if (!entry || !entry.available) { showNotice(`There is no available ${version.toUpperCase()} address to copy.`); return; }
  try { await navigator.clipboard.writeText(entry.address); button.innerHTML = "Copied <span>✓</span>"; setTimeout(() => { button.innerHTML = "Copy <span>□</span>"; }, 1400); }
  catch (error) { showNotice("Clipboard access is unavailable in this browser."); }
}

$("check-button").addEventListener("click", loadInfo);
$("refresh-button").addEventListener("click", loadInfo);
document.querySelectorAll(".copy-button").forEach((button) => button.addEventListener("click", () => copyAddress(button.dataset.copy, button)));
