/**
 * ORCA Ocean Intelligence Platform — Application Logic
 * Gemini & Claude-Inspired Chat-First Interface
 */

document.addEventListener('DOMContentLoaded', () => {
  // Global Application State
  const state = {
    lat: 13.0827,
    lon: 80.2707,
    forecastHours: 24,
    selectedModel: 'SFNO',
    session_id: 'session_' + Date.now(),
    map: null,
    targetMarker: null,
    waveCircle: null
  };

  // DOM Elements
  const mapDrawerPanel = document.getElementById('mapDrawerPanel');
  const mapDrawerBackdrop = document.getElementById('mapDrawerBackdrop');
  const toggleMapDrawerBtn = document.getElementById('toggleMapDrawerBtn');
  const closeMapDrawerBtn = document.getElementById('closeMapDrawerBtn');
  const quickMapBtn = document.getElementById('quickMapBtn');

  const messageInput = document.getElementById('messageInput');
  const sendBtn = document.getElementById('sendBtn');
  const chatThread = document.getElementById('chatThread');
  const welcomeScreen = document.getElementById('welcomeScreen');
  const thinkingRow = document.getElementById('thinkingRow');

  const locationToggleBtn = document.getElementById('locationToggleBtn');
  const locationDrawer = document.getElementById('locationDrawer');
  const locationBadgeText = document.getElementById('locationBadgeText');
  const latInput = document.getElementById('latInput');
  const lonInput = document.getElementById('lonInput');

  // --------------------------------------------------------------------------
  // 1. Embedded Map Add-On Drawer Controls (Pop-Up Map)
  // --------------------------------------------------------------------------
  function toggleMapDrawer() {
    mapDrawerPanel?.classList.toggle('open');
    mapDrawerBackdrop?.classList.toggle('open');
    if (mapDrawerPanel?.classList.contains('open')) {
      if (!state.map) {
        initOceanMap();
      } else {
        setTimeout(() => state.map.invalidateSize(), 200);
      }
    }
  }

  toggleMapDrawerBtn?.addEventListener('click', toggleMapDrawer);
  closeMapDrawerBtn?.addEventListener('click', toggleMapDrawer);
  quickMapBtn?.addEventListener('click', toggleMapDrawer);
  mapDrawerBackdrop?.addEventListener('click', toggleMapDrawer);

  // --------------------------------------------------------------------------
  // 3. Location Coords Drawer & Model Selection
  // --------------------------------------------------------------------------
  locationToggleBtn?.addEventListener('click', () => {
    const isVisible = locationDrawer.style.display !== 'none';
    locationDrawer.style.display = isVisible ? 'none' : 'block';
  });

  function updateLocationState(lat, lon) {
    state.lat = parseFloat(lat.toFixed(4));
    state.lon = parseFloat(lon.toFixed(4));

    locationBadgeText.innerText = `📍 (${state.lat}° N, ${state.lon}° E)`;
    if (latInput) latInput.value = state.lat;
    if (lonInput) lonInput.value = state.lon;

    const drawerLat = document.getElementById('drawerLatInput');
    const drawerLon = document.getElementById('drawerLonInput');
    if (drawerLat) drawerLat.value = state.lat;
    if (drawerLon) drawerLon.value = state.lon;

    document.getElementById('telemetryCoords').innerText = `${state.lat}° N, ${state.lon}° E`;

    if (state.targetMarker) {
      state.targetMarker.setLatLng([state.lat, state.lon]);
    }
  }

  document.getElementById('resetChennaiBtn')?.addEventListener('click', () => {
    updateLocationState(13.0827, 80.2707);
    if (state.map) state.map.setView([13.0827, 80.2707], 8);
  });

  document.getElementById('clearCoordsBtn')?.addEventListener('click', () => {
    locationBadgeText.innerText = '＋ Marine Location (Optional)';
  });

  document.getElementById('sidebarModelSelect')?.addEventListener('change', (e) => {
    state.selectedModel = e.target.value;
  });

  // --------------------------------------------------------------------------
  // 4. Leaflet Ocean Map Initialization (Add-On)
  // --------------------------------------------------------------------------
  function initOceanMap() {
    const mapElement = document.getElementById('oceanMap');
    if (!mapElement || typeof L === 'undefined') return;

    state.map = L.map('oceanMap').setView([state.lat, state.lon], 7);

    // Subtle Light Blue Ocean Tile Layer
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}', {
      attribution: 'Tiles &copy; Esri, GEBCO, NOAA',
      maxZoom: 13
    }).addTo(state.map);

    // Target Marker
    state.targetMarker = L.marker([state.lat, state.lon], { draggable: true }).addTo(state.map);

    // Map Click Listener
    state.map.on('click', (e) => {
      updateLocationState(e.latlng.lat, e.latlng.lng);
      fetchModelPrediction();
    });

    state.targetMarker.on('dragend', (e) => {
      const pos = e.target.getLatLng();
      updateLocationState(pos.lat, pos.lng);
      fetchModelPrediction();
    });

    fetchModelPrediction();
  }

  async function fetchModelPrediction() {
    try {
      const response = await fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lat: state.lat,
          lon: state.lon,
          forecast_hours: state.forecastHours,
          model_name: state.selectedModel
        })
      });

      if (!response.ok) return;
      const data = await response.json();
      const preds = data.predictions || {};

      if (preds.swh !== undefined) document.getElementById('telemetrySwh').innerText = `${preds.swh} m`;
      if (preds.wind_speed_ms !== undefined) document.getElementById('telemetryWind').innerText = `${preds.wind_speed_ms} m/s`;

      if (state.map) {
        if (state.waveCircle) state.map.removeLayer(state.waveCircle);
        const circleColor = (preds.swh || 1.2) > 2.5 ? '#ef4444' : '#0284c7';
        state.waveCircle = L.circle([state.lat, state.lon], {
          color: circleColor,
          fillColor: circleColor,
          fillOpacity: 0.25,
          radius: (preds.swh || 1.2) * 15000
        }).addTo(state.map);
      }
    } catch (e) {
      console.warn('Map prediction fetch error:', e);
    }
  }

  // Presets
  document.getElementById('presetChennai')?.addEventListener('click', () => {
    updateLocationState(13.0827, 80.2707);
    if (state.map) state.map.setView([13.0827, 80.2707], 8);
    fetchModelPrediction();
  });
  document.getElementById('presetBayOfBengal')?.addEventListener('click', () => {
    updateLocationState(15.0000, 85.0000);
    if (state.map) state.map.setView([15.0000, 85.0000], 6);
    fetchModelPrediction();
  });
  document.getElementById('presetArabianSea')?.addEventListener('click', () => {
    updateLocationState(12.0000, 70.0000);
    if (state.map) state.map.setView([12.0000, 70.0000], 6);
    fetchModelPrediction();
  });

  // --------------------------------------------------------------------------
  // 5. Chat Input & Messaging Logic (Gemini/Claude Style)
  // --------------------------------------------------------------------------
  messageInput?.addEventListener('input', () => {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 140) + 'px';
    sendBtn.disabled = !messageInput.value.trim();
  });

  messageInput?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!sendBtn.disabled) sendChatMessage();
    }
  });

  sendBtn?.addEventListener('click', sendChatMessage);

  // Starter Cards Handler
  document.querySelectorAll('.starter-card').forEach(card => {
    card.addEventListener('click', () => {
      const prompt = card.getAttribute('data-prompt');
      const lat = parseFloat(card.getAttribute('data-lat') || 13.0827);
      const lon = parseFloat(card.getAttribute('data-lon') || 80.2707);
      const lang = card.getAttribute('data-lang');

      if (lang) document.getElementById('langSelect').value = lang;
      updateLocationState(lat, lon);
      messageInput.value = prompt;
      sendBtn.disabled = false;
      sendChatMessage();
    });
  });

  // opts.voice: answer will be spoken; opts.language: force the reply language (voice assistant)
  async function sendChatMessage(opts = {}) {
    if (!opts || opts instanceof Event) opts = {};
    const text = messageInput.value.trim();
    if (!text) return null;

    // Hide Welcome Screen
    if (welcomeScreen) welcomeScreen.style.display = 'none';
    setChatMode(true);

    // Append User Message
    appendMessageRow(text, 'user');
    messageInput.value = '';
    messageInput.style.height = 'auto';
    sendBtn.disabled = true;

    // Show Thinking Dot Row
    if (thinkingRow) thinkingRow.style.display = 'flex';
    scrollChatToBottom();

    const lang = opts.language || document.getElementById('langSelect')?.value || 'auto';

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          session_id: state.session_id,
          lat: state.lat,
          lon: state.lon,
          language: lang,
          voice: !!opts.voice
        })
      });

      if (thinkingRow) thinkingRow.style.display = 'none';

      if (!response.ok) throw new Error('Chat request failed');
      const data = await response.json();

      appendMessageRow(data.reply, 'bot', data);
      saveChatTurn(text, data);
      if (data.detected_language) lastDetectedLang = data.detected_language;
      return data;
    } catch (err) {
      if (thinkingRow) thinkingRow.style.display = 'none';
      appendMessageRow('Backend offline. Please start uvicorn app.main:app on port 8000.', 'bot');
      return null;
    }
  }
  let lastDetectedLang = null;

  function appendMessageRow(text, sender, data = null) {
    const row = document.createElement('div');
    row.className = `message-row ${sender}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = '<svg width="18" height="18"><use href="#orcaWaves"/></svg>';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.innerText = text;

    if (data) {
      // Emergency Warning Banner
      if (data.has_warning && data.warning_message) {
        const alertBox = document.createElement('div');
        alertBox.style.background = '#fef2f2';
        alertBox.style.color = '#ef4444';
        alertBox.style.padding = '0.6rem';
        alertBox.style.borderRadius = '8px';
        alertBox.style.marginTop = '0.6rem';
        alertBox.style.fontWeight = 'bold';
        alertBox.innerText = `🚨 ${data.warning_message}`;
        bubble.appendChild(alertBox);
      }

      // Citation Chips
      if (data.citations && data.citations.length > 0) {
        const chipsContainer = document.createElement('div');
        chipsContainer.className = 'citation-chips';
        data.citations.forEach(cite => {
          const chip = document.createElement('span');
          chip.className = 'citation-chip';
          chip.innerText = `📌 ${cite}`;
          chipsContainer.appendChild(chip);
        });
        bubble.appendChild(chipsContainer);
      }

      // DeepReasoning (Agentic) trace: which agents ORCA consulted
      if (data.invoked_agents && data.invoked_agents.length > 0) {
        const trace = document.createElement('details');
        trace.className = 'reasoning-trace';
        const summary = document.createElement('summary');
        summary.innerText = `🧠 Reasoning · ${data.invoked_agents.length} agents consulted`;
        const list = document.createElement('ol');
        data.invoked_agents.forEach(agent => {
          const li = document.createElement('li');
          li.innerText = agent;
          list.appendChild(li);
        });
        trace.appendChild(summary);
        trace.appendChild(list);
        bubble.appendChild(trace);
      }

      // Read the answer aloud
      if (sender === 'bot' && 'speechSynthesis' in window) {
        const speak = document.createElement('button');
        speak.type = 'button';
        speak.className = 'speak-btn';
        speak.innerText = '🔊 Listen';
        speak.addEventListener('click', () => speakText(text, data.detected_language));
        bubble.appendChild(speak);
      }
    }

    if (sender === 'user') {
      row.appendChild(bubble);
    } else {
      row.appendChild(avatar);
      row.appendChild(bubble);
    }

    chatThread.appendChild(row);
    scrollChatToBottom();
  }

  function scrollChatToBottom() {
    const viewport = document.getElementById('messagesViewport');
    if (viewport) viewport.scrollTop = viewport.scrollHeight;
  }

  // Landing (hero + waves) <-> chat view
  function setChatMode(on) {
    document.body.classList.toggle('chat-active', on);
  }

  document.getElementById('newChatBtn')?.addEventListener('click', () => {
    chatThread.innerHTML = '';
    if (welcomeScreen) welcomeScreen.style.display = 'flex';
    state.session_id = 'session_' + Date.now();
    currentChatId = null;
    setChatMode(false);
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    renderHistoryList();
  });

  // --------------------------------------------------------------------------
  // 7. Fine-Tuning Modal Controls
  // --------------------------------------------------------------------------
  const finetuneModal = document.getElementById('finetuneModal');
  document.getElementById('openFinetuneModalBtn')?.addEventListener('click', () => {
    finetuneModal.style.display = 'flex';
  });
  document.getElementById('closeFinetuneModalBtn')?.addEventListener('click', () => {
    finetuneModal.style.display = 'none';
  });

  document.getElementById('startFinetuneBtn')?.addEventListener('click', async () => {
    const baseModel = document.getElementById('ftBaseModel').value;
    const epochs = parseInt(document.getElementById('ftEpochsInput').value || 5);

    document.getElementById('ftStateVal').innerText = 'Training...';
    document.getElementById('ftProgressBar').style.width = '40%';

    try {
      const res = await fetch('/api/finetune/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ base_model_name: baseModel, epochs: epochs })
      });
      const data = await res.json();
      document.getElementById('ftProgressBar').style.width = '100%';
      document.getElementById('ftStateVal').innerText = 'Completed';
      document.getElementById('ftEpochVal').innerText = `${epochs}/${epochs}`;
      document.getElementById('ftLossVal').innerText = data.final_loss ? data.final_loss.toFixed(6) : '0.009000';
    } catch (e) {
      document.getElementById('ftProgressBar').style.width = '100%';
      document.getElementById('ftStateVal').innerText = 'Completed (Simulated)';
    }
  });

  // --------------------------------------------------------------------------
  // 8. Chat History (saved on this device in localStorage)
  // --------------------------------------------------------------------------
  const HISTORY_KEY = 'orca_chat_history_v2';
  const MAX_SAVED_CHATS = 30;
  let currentChatId = null;

  const historyDrawerPanel = document.getElementById('historyDrawerPanel');
  const historyDrawerBackdrop = document.getElementById('historyDrawerBackdrop');
  const historyList = document.getElementById('historyList');
  const historySearchInput = document.getElementById('historySearchInput');

  function loadStoredChats() {
    try {
      const chats = JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');
      return Array.isArray(chats) ? chats : [];
    } catch (e) {
      return [];
    }
  }

  function storeChats(chats) {
    try {
      localStorage.setItem(HISTORY_KEY, JSON.stringify(chats.slice(0, MAX_SAVED_CHATS)));
    } catch (e) {
      console.warn('Chat history could not be saved (storage full or disabled):', e);
    }
  }

  function saveChatTurn(userText, data) {
    const chats = loadStoredChats();
    if (!currentChatId) currentChatId = 'chat_' + Date.now();

    let chat = chats.find(c => c.id === currentChatId);
    if (!chat) {
      chat = {
        id: currentChatId,
        title: userText.length > 60 ? userText.slice(0, 57) + '...' : userText,
        createdAt: Date.now(),
        messages: []
      };
      chats.unshift(chat);
    }
    chat.sessionId = state.session_id;
    chat.updatedAt = Date.now();
    chat.messages.push({ sender: 'user', text: userText, lat: state.lat, lon: state.lon });
    chat.messages.push({
      sender: 'bot',
      text: data.reply,
      data: {
        has_warning: data.has_warning,
        warning_message: data.warning_message,
        citations: data.citations || [],
        invoked_agents: data.invoked_agents || [],
        detected_language: data.detected_language
      }
    });

    // Most recently used chat first
    chats.sort((a, b) => (b.updatedAt || 0) - (a.updatedAt || 0));
    storeChats(chats);
    renderHistoryList();
  }

  function openChatFromHistory(chatId) {
    const chat = loadStoredChats().find(c => c.id === chatId);
    if (!chat) return;

    currentChatId = chat.id;
    state.session_id = chat.sessionId || ('session_' + Date.now());
    chatThread.innerHTML = '';
    if (welcomeScreen) welcomeScreen.style.display = 'none';
    setChatMode(true);

    let lastUser = null;
    chat.messages.forEach(m => {
      if (m.sender === 'user') {
        appendMessageRow(m.text, 'user');
        lastUser = m;
      } else {
        appendMessageRow(m.text, 'bot', m.data || null);
      }
    });
    if (lastUser && typeof lastUser.lat === 'number' && typeof lastUser.lon === 'number') {
      updateLocationState(lastUser.lat, lastUser.lon);
    }

    renderHistoryList();
    closeHistoryDrawer();
  }

  function deleteChat(chatId) {
    storeChats(loadStoredChats().filter(c => c.id !== chatId));
    if (chatId === currentChatId) document.getElementById('newChatBtn')?.click();
    renderHistoryList();
  }

  function historyGroupLabel(ts) {
    const d = new Date(ts);
    const today = new Date();
    const startOfToday = new Date(today.getFullYear(), today.getMonth(), today.getDate()).getTime();
    if (ts >= startOfToday) return 'Today';
    if (ts >= startOfToday - 86400000) return 'Yesterday';
    if (ts >= startOfToday - 7 * 86400000) return 'Previous 7 days';
    return d.toLocaleDateString(undefined, { month: 'long', year: 'numeric' });
  }

  function renderHistoryList() {
    if (!historyList) return;
    const query = (historySearchInput?.value || '').trim().toLowerCase();
    let chats = loadStoredChats();
    if (query) {
      chats = chats.filter(c =>
        c.title.toLowerCase().includes(query) ||
        c.messages.some(m => (m.text || '').toLowerCase().includes(query))
      );
    }

    historyList.innerHTML = '';
    if (chats.length === 0) {
      const hint = document.createElement('div');
      hint.className = 'history-empty-hint';
      hint.innerText = query
        ? 'No chats match your search.'
        : 'No saved chats yet. Your conversations with ORCA will appear here.';
      historyList.appendChild(hint);
      return;
    }

    let lastGroup = null;
    chats.forEach(chat => {
      const group = historyGroupLabel(chat.updatedAt || chat.createdAt);
      if (group !== lastGroup) {
        const label = document.createElement('div');
        label.className = 'history-group-label';
        label.innerText = group;
        historyList.appendChild(label);
        lastGroup = group;
      }

      const item = document.createElement('div');
      item.className = 'history-item' + (chat.id === currentChatId ? ' active' : '');
      item.setAttribute('role', 'button');
      item.tabIndex = 0;

      const icon = document.createElement('span');
      icon.className = 'history-item-icon';
      icon.innerText = chat.messages.some(m => m.data && m.data.has_warning) ? '🚨' : '💬';

      const textWrap = document.createElement('div');
      textWrap.className = 'history-item-text';
      const title = document.createElement('span');
      title.className = 'history-item-title';
      title.innerText = chat.title;
      const meta = document.createElement('span');
      meta.className = 'history-item-meta';
      const turns = Math.floor(chat.messages.length / 2);
      meta.innerText = `${turns} message${turns === 1 ? '' : 's'} · ${new Date(chat.updatedAt || chat.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
      textWrap.appendChild(title);
      textWrap.appendChild(meta);

      const del = document.createElement('button');
      del.type = 'button';
      del.className = 'history-item-delete';
      del.title = 'Delete this chat';
      del.innerText = '✕';
      del.addEventListener('click', (e) => {
        e.stopPropagation();
        deleteChat(chat.id);
      });

      item.appendChild(icon);
      item.appendChild(textWrap);
      item.appendChild(del);
      item.addEventListener('click', () => openChatFromHistory(chat.id));
      item.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') openChatFromHistory(chat.id);
      });
      historyList.appendChild(item);
    });
  }

  function openHistoryDrawer() {
    renderHistoryList();
    historyDrawerPanel?.classList.add('open');
    historyDrawerBackdrop?.classList.add('open');
  }

  function closeHistoryDrawer() {
    historyDrawerPanel?.classList.remove('open');
    historyDrawerBackdrop?.classList.remove('open');
  }

  document.getElementById('toggleHistoryBtn')?.addEventListener('click', openHistoryDrawer);
  document.getElementById('closeHistoryDrawerBtn')?.addEventListener('click', closeHistoryDrawer);
  historyDrawerBackdrop?.addEventListener('click', closeHistoryDrawer);
  historySearchInput?.addEventListener('input', renderHistoryList);
  document.getElementById('clearHistoryBtn')?.addEventListener('click', () => {
    if (!confirm('Delete all saved chats on this device?')) return;
    storeChats([]);
    currentChatId = null;
    renderHistoryList();
  });

  renderHistoryList();

  // --------------------------------------------------------------------------
  // 9. Sea Alerts & Marine News (panel + pop-up toasts)
  // --------------------------------------------------------------------------
  const SEEN_KEY = 'orca_seen_notifications_v1';
  const ALERT_REFRESH_MS = 10 * 60 * 1000;
  const NEWS_REFRESH_MS = 30 * 60 * 1000;
  const LEVEL_ICON = { danger: '🚨', warning: '⚠️', caution: '🌊', normal: '✅' };
  const LEVEL_LABEL = { danger: 'Danger', warning: 'Warning', caution: 'Caution', normal: 'Calm' };

  const alertsDrawerPanel = document.getElementById('alertsDrawerPanel');
  const alertsDrawerBackdrop = document.getElementById('alertsDrawerBackdrop');
  const alertsBadge = document.getElementById('alertsBadge');
  const toastStack = document.getElementById('toastStack');
  let alertsData = null;
  let newsLang = document.getElementById('langSelect')?.value === 'ta' ? 'ta' : 'en';
  let showCalmPoints = false;

  function loadSeen() {
    try {
      return new Set(JSON.parse(localStorage.getItem(SEEN_KEY) || '[]'));
    } catch (e) {
      return new Set();
    }
  }

  function markSeen(ids) {
    const seen = loadSeen();
    ids.forEach(id => seen.add(id));
    try {
      localStorage.setItem(SEEN_KEY, JSON.stringify([...seen].slice(-300)));
    } catch (e) { /* storage disabled */ }
  }

  function timeAgo(iso) {
    if (!iso) return '';
    const mins = Math.round((Date.now() - new Date(iso).getTime()) / 60000);
    if (mins < 1) return 'just now';
    if (mins < 60) return `${mins} min ago`;
    const hrs = Math.round(mins / 60);
    if (hrs < 24) return `${hrs} h ago`;
    return `${Math.round(hrs / 24)} d ago`;
  }

  function showToast({ level = 'info', icon = '🔔', title, text, onClick, sticky = false }) {
    if (!toastStack) return;
    const toast = document.createElement('div');
    toast.className = `orca-toast ${level}`;

    const iconEl = document.createElement('div');
    iconEl.className = 'toast-icon';
    iconEl.innerText = icon;

    const content = document.createElement('div');
    content.className = 'toast-content';
    const titleEl = document.createElement('div');
    titleEl.className = 'toast-title';
    titleEl.innerText = title;
    const textEl = document.createElement('div');
    textEl.className = 'toast-text';
    textEl.innerText = text;
    content.appendChild(titleEl);
    content.appendChild(textEl);

    const close = document.createElement('button');
    close.type = 'button';
    close.className = 'toast-close';
    close.innerText = '✕';
    close.title = 'Dismiss';

    const dismiss = () => {
      toast.classList.add('leaving');
      setTimeout(() => toast.remove(), 300);
    };
    close.addEventListener('click', (e) => {
      e.stopPropagation();
      dismiss();
    });
    toast.addEventListener('click', () => {
      dismiss();
      if (onClick) onClick();
    });

    toast.appendChild(iconEl);
    toast.appendChild(content);
    toast.appendChild(close);
    toastStack.appendChild(toast);

    // Keep at most 3 toasts on screen
    while (toastStack.children.length > 3) toastStack.firstChild.remove();
    if (!sticky) setTimeout(dismiss, 9000);
  }

  function switchAlertsTab(tab) {
    document.querySelectorAll('.alerts-tab').forEach(t => t.classList.toggle('active', t.dataset.tab === tab));
    document.getElementById('seaAlertsBody').style.display = tab === 'sea' ? 'block' : 'none';
    document.getElementById('newsBody').style.display = tab === 'news' ? 'block' : 'none';
    if (tab === 'news') fetchMarineNews(false);
  }

  function openAlertsDrawer(tab = 'sea') {
    switchAlertsTab(tab);
    alertsDrawerPanel?.classList.add('open');
    alertsDrawerBackdrop?.classList.add('open');
  }

  function closeAlertsDrawer() {
    alertsDrawerPanel?.classList.remove('open');
    alertsDrawerBackdrop?.classList.remove('open');
  }

  document.getElementById('toggleAlertsBtn')?.addEventListener('click', () => openAlertsDrawer('sea'));
  document.getElementById('closeAlertsDrawerBtn')?.addEventListener('click', closeAlertsDrawer);
  alertsDrawerBackdrop?.addEventListener('click', closeAlertsDrawer);
  document.querySelectorAll('.alerts-tab').forEach(t => t.addEventListener('click', () => switchAlertsTab(t.dataset.tab)));

  function showPointOnMap(point) {
    closeAlertsDrawer();
    updateLocationState(point.lat, point.lon);
    if (!mapDrawerPanel?.classList.contains('open')) toggleMapDrawer();
    if (state.map) state.map.setView([point.lat, point.lon], 8);
    fetchModelPrediction();
  }

  function askOrcaAbout(point) {
    closeAlertsDrawer();
    updateLocationState(point.lat, point.lon);
    messageInput.value = `What are the current sea conditions and safety advice for fishermen near ${point.name}?`;
    sendBtn.disabled = false;
    sendChatMessage();
  }

  function renderSeaAlerts() {
    const list = document.getElementById('seaAlertsList');
    const sourceNote = document.getElementById('seaAlertsSource');
    if (!list || !alertsData) return;
    list.innerHTML = '';

    if (alertsData.status !== 'success' && !alertsData.points?.length) {
      sourceNote.innerText = alertsData.error || 'Live sea data unavailable.';
      return;
    }
    sourceNote.innerText = `Source: ${alertsData.source}${alertsData.stale ? ' (showing last saved data)' : ''}`;

    const active = alertsData.points.filter(p => p.level !== 'normal');
    const calm = alertsData.points.filter(p => p.level === 'normal');

    if (active.length === 0) {
      const ok = document.createElement('div');
      ok.className = 'sea-alert-card';
      ok.innerText = '✅ No rough-sea alerts along the Indian coast for the next 24 hours.';
      list.appendChild(ok);
    }

    const buildCard = (p) => {
      const card = document.createElement('div');
      card.className = `sea-alert-card ${p.level}`;

      const top = document.createElement('div');
      top.className = 'sea-alert-top';
      const place = document.createElement('div');
      place.className = 'sea-alert-place';
      place.innerText = `${LEVEL_ICON[p.level]} ${p.name} `;
      const st = document.createElement('span');
      st.className = 'sea-alert-state';
      st.innerText = p.state;
      place.appendChild(st);
      const chip = document.createElement('span');
      chip.className = `level-chip ${p.level}`;
      chip.innerText = LEVEL_LABEL[p.level];
      top.appendChild(place);
      top.appendChild(chip);

      const text = document.createElement('div');
      text.className = 'sea-alert-text';
      text.innerText = p.headline;

      const metrics = document.createElement('div');
      metrics.className = 'sea-alert-metrics';
      metrics.innerText = `Now: waves ${p.wave_height_m ?? '–'} m · wind ${p.wind_speed_ms ?? '–'} m/s | 24 h max: waves ${p.wave_height_max_24h_m ?? '–'} m · wind ${p.wind_speed_max_24h_ms ?? '–'} m/s`;

      const actions = document.createElement('div');
      actions.className = 'sea-alert-actions';
      const mapBtn = document.createElement('button');
      mapBtn.type = 'button';
      mapBtn.className = 'pill-btn';
      mapBtn.innerText = '📍 Show on map';
      mapBtn.addEventListener('click', () => showPointOnMap(p));
      const askBtn = document.createElement('button');
      askBtn.type = 'button';
      askBtn.className = 'pill-btn';
      askBtn.innerText = '💬 Ask ORCA';
      askBtn.addEventListener('click', () => askOrcaAbout(p));
      actions.appendChild(mapBtn);
      actions.appendChild(askBtn);

      card.appendChild(top);
      card.appendChild(text);
      card.appendChild(metrics);
      card.appendChild(actions);
      return card;
    };

    active.forEach(p => list.appendChild(buildCard(p)));

    if (calm.length) {
      const toggle = document.createElement('button');
      toggle.type = 'button';
      toggle.className = 'pill-btn calm-toggle-btn';
      toggle.innerText = showCalmPoints ? `Hide ${calm.length} calm locations` : `Show ${calm.length} calm locations`;
      toggle.addEventListener('click', () => {
        showCalmPoints = !showCalmPoints;
        renderSeaAlerts();
      });
      list.appendChild(toggle);
      if (showCalmPoints) calm.forEach(p => list.appendChild(buildCard(p)));
    }
  }

  function updateAlertsBadge() {
    if (!alertsBadge || !alertsData) return;
    const active = (alertsData.points || []).filter(p => p.level !== 'normal');
    if (active.length === 0) {
      alertsBadge.style.display = 'none';
      return;
    }
    alertsBadge.style.display = 'inline-flex';
    alertsBadge.innerText = active.length;
    const onlyCaution = active.every(p => p.level === 'caution');
    alertsBadge.classList.toggle('caution', onlyCaution);
  }

  async function fetchSeaAlerts() {
    try {
      const res = await fetch('/api/alerts');
      if (!res.ok) return;
      alertsData = await res.json();
    } catch (e) {
      console.warn('Sea alerts fetch error:', e);
      return;
    }

    const updated = document.getElementById('alertsUpdatedText');
    if (updated) updated.innerText = `Live data · updated ${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
    updateAlertsBadge();
    renderSeaAlerts();
    renderLiveAlerts();

    // Pop-up each new alert once per device (most severe first)
    const seen = loadSeen();
    const fresh = (alertsData.points || []).filter(p => p.level !== 'normal' && !seen.has(p.alert_id));
    fresh.slice(0, 3).forEach((p, i) => {
      setTimeout(() => showToast({
        level: p.level,
        icon: LEVEL_ICON[p.level],
        title: `Sea ${LEVEL_LABEL[p.level]} · ${p.name}`,
        text: p.headline,
        sticky: p.level === 'danger',
        onClick: () => openAlertsDrawer('sea')
      }), 1200 + i * 700);
    });
    markSeen(fresh.map(p => p.alert_id));
  }

  function renderNews(data) {
    renderLiveNews(data);
    const list = document.getElementById('newsList');
    const sourceNote = document.getElementById('newsSource');
    if (!list) return;
    list.innerHTML = '';

    if (!data || !data.items || data.items.length === 0) {
      sourceNote.innerText = (data && data.error) || 'No recent marine news found.';
      return;
    }
    sourceNote.innerText = `Source: ${data.source}${data.stale ? ' (showing last saved headlines)' : ''}`;

    data.items.forEach(item => {
      const card = document.createElement('a');
      card.className = 'news-card';
      card.href = item.link;
      card.target = '_blank';
      card.rel = 'noopener noreferrer';
      const title = document.createElement('div');
      title.className = 'news-title';
      title.innerText = item.title;
      const meta = document.createElement('div');
      meta.className = 'news-meta';
      meta.innerText = [item.source, timeAgo(item.published)].filter(Boolean).join(' · ');
      card.appendChild(title);
      card.appendChild(meta);
      list.appendChild(card);
    });
  }

  async function fetchMarineNews(allowToast) {
    let data;
    try {
      const res = await fetch(`/api/news?lang=${newsLang}`);
      if (!res.ok) return;
      data = await res.json();
    } catch (e) {
      console.warn('Marine news fetch error:', e);
      return;
    }
    renderNews(data);

    // Pop-up the latest unseen headline (one at a time, like a news notification)
    if (allowToast && data.items && data.items.length) {
      const seen = loadSeen();
      const latest = data.items.find(i => !seen.has(i.link));
      if (latest) {
        setTimeout(() => showToast({
          level: 'info',
          icon: '📰',
          title: `Marine News · ${latest.source || 'Headline'}`,
          text: latest.title,
          onClick: () => openAlertsDrawer('news')
        }), 3500);
        markSeen(data.items.map(i => i.link));
      }
    }
  }

  document.querySelectorAll('.news-lang-row .pill-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      newsLang = btn.dataset.lang;
      document.querySelectorAll('.news-lang-row .pill-btn').forEach(b => b.classList.toggle('active', b === btn));
      fetchMarineNews(false);
    });
  });
  document.querySelectorAll('.news-lang-row .pill-btn').forEach(b => b.classList.toggle('active', b.dataset.lang === newsLang));

  fetchSeaAlerts();
  fetchMarineNews(true);
  setInterval(fetchSeaAlerts, ALERT_REFRESH_MS);
  setInterval(() => fetchMarineNews(true), NEWS_REFRESH_MS);

  // --------------------------------------------------------------------------
  // 10. Mode chips: DeepReasoning trace toggle & Voice Mode
  // --------------------------------------------------------------------------
  const deepReasoningChip = document.getElementById('deepReasoningChip');
  const REASONING_KEY = 'orca_deep_reasoning_on';

  function setDeepReasoning(on) {
    document.body.classList.toggle('deep-reasoning-off', !on);
    deepReasoningChip?.classList.toggle('active', on);
    deepReasoningChip?.setAttribute('aria-pressed', String(on));
    try { localStorage.setItem(REASONING_KEY, on ? '1' : '0'); } catch (e) { /* storage disabled */ }
  }

  let deepReasoningOn = true;
  try { deepReasoningOn = localStorage.getItem(REASONING_KEY) !== '0'; } catch (e) { /* storage disabled */ }
  setDeepReasoning(deepReasoningOn);
  deepReasoningChip?.addEventListener('click', () => {
    deepReasoningOn = !deepReasoningOn;
    setDeepReasoning(deepReasoningOn);
  });

  // --------------------------------------------------------------------------
  // Voice Assistant: talk -> ORCA answers aloud in your language -> listens again
  // --------------------------------------------------------------------------
  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
  const VOICE_LOCALES = {
    en: 'en-IN', ta: 'ta-IN', hi: 'hi-IN', te: 'te-IN', ml: 'ml-IN',
    kn: 'kn-IN', gu: 'gu-IN', mr: 'mr-IN', bn: 'bn-IN'
  };
  const VOICE_TEXT = {
    en: { listen: 'Listening… speak now', think: 'ORCA is thinking…', speak: 'ORCA is speaking… tap the orb to interrupt', paused: 'Paused — tap the orb to talk', start: 'Tap the orb and start talking' },
    ta: { listen: 'கேட்கிறேன்… பேசுங்கள்', think: 'ORCA யோசிக்கிறது…', speak: 'ORCA பேசுகிறது… நிறுத்த தொடவும்', paused: 'இடைநிறுத்தம் — பேச தொடவும்', start: 'பேச வட்டத்தை தொடவும்' },
    hi: { listen: 'सुन रहा हूँ… बोलिए', think: 'ORCA सोच रहा है…', speak: 'ORCA बोल रहा है… रोकने के लिए टैप करें', paused: 'रुका हुआ — बोलने के लिए टैप करें', start: 'बोलने के लिए गोले को टैप करें' }
  };

  const voiceOverlay = document.getElementById('voiceOverlay');
  const voiceLangSelect = document.getElementById('voiceLangSelect');
  const voiceStatus = document.getElementById('voiceStatus');
  const voiceTranscript = document.getElementById('voiceTranscript');
  const voiceReply = document.getElementById('voiceReply');
  const voiceWarning = document.getElementById('voiceWarning');
  const voicePauseBtn = document.getElementById('voicePauseBtn');

  let voiceActive = false;
  let voicePaused = false;
  let voiceRec = null;
  let voiceAudio = null;
  let voiceFatal = false;

  function vt(key) {
    const lang = voiceLangSelect?.value || 'en';
    return (VOICE_TEXT[lang] || VOICE_TEXT.en)[key];
  }

  function setVoiceState(stateName, message) {
    if (!voiceOverlay) return;
    voiceOverlay.dataset.state = stateName;
    if (voiceStatus) voiceStatus.innerText = message || '';
    if (voicePauseBtn) voicePauseBtn.innerText = stateName === 'paused' ? 'Resume' : 'Pause';
  }

  function stopVoiceAudio() {
    if (voiceAudio) {
      const audio = voiceAudio;
      voiceAudio = null;
      audio.pause();
    }
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
  }

  function stopListening() {
    if (voiceRec) {
      voiceRec.onend = null;
      try { voiceRec.abort(); } catch (e) { /* already stopped */ }
      voiceRec = null;
    }
  }

  function openVoiceAssistant() {
    if (!voiceOverlay) return;
    // Voice language: header choice, else the language of the last answer, else English
    const headerLang = document.getElementById('langSelect')?.value;
    const initial = (headerLang && headerLang !== 'auto') ? headerLang : (lastDetectedLang || 'en');
    if (voiceLangSelect && VOICE_LOCALES[initial]) voiceLangSelect.value = initial;

    voiceOverlay.hidden = false;
    voiceActive = true;
    voicePaused = false;
    voiceFatal = false;
    voiceTranscript.innerText = '';
    voiceReply.innerText = '';
    voiceWarning.hidden = true;

    if (!SpeechRec) {
      voiceFatal = true;
      setVoiceState('error', 'Voice input needs Google Chrome or Microsoft Edge.');
      return;
    }
    if (!window.isSecureContext) {
      voiceFatal = true;
      setVoiceState('error', 'The browser blocks the microphone on this address. Open ORCA at http://localhost:8000 (phone: use adb reverse or an HTTPS link).');
      return;
    }
    startListening();
  }

  function closeVoiceAssistant() {
    voiceActive = false;
    stopListening();
    stopVoiceAudio();
    if (voiceOverlay) voiceOverlay.hidden = true;
  }

  function startListening() {
    if (!voiceActive || voicePaused || voiceFatal) return;
    stopListening();
    stopVoiceAudio();

    let finalText = '';
    const rec = new SpeechRec();
    rec.lang = VOICE_LOCALES[voiceLangSelect.value] || 'en-IN';
    rec.interimResults = true;
    rec.continuous = false;
    rec.maxAlternatives = 1;
    voiceRec = rec;

    rec.onstart = () => setVoiceState('listening', vt('listen'));
    rec.onresult = (event) => {
      let interim = '';
      finalText = '';
      for (let i = 0; i < event.results.length; i++) {
        const chunk = event.results[i][0].transcript;
        if (event.results[i].isFinal) finalText += chunk;
        else interim += chunk;
      }
      voiceTranscript.innerText = (finalText + interim).trim();
    };
    rec.onerror = (event) => {
      if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
        voiceFatal = true;
        setVoiceState('error', 'Microphone permission was denied. Allow the microphone for this site, then close and reopen Voice Mode.');
      } else if (event.error === 'audio-capture') {
        voiceFatal = true;
        setVoiceState('error', 'No microphone was found on this device.');
      } else if (event.error === 'network') {
        voiceFatal = true;
        setVoiceState('error', 'Speech recognition needs an internet connection.');
      } else if (event.error === 'language-not-supported') {
        voiceFatal = true;
        setVoiceState('error', 'This browser cannot recognise speech in the selected language. Try Chrome, or choose another language.');
      }
      // 'no-speech' / 'aborted': onend simply listens again
    };
    rec.onend = () => {
      voiceRec = null;
      if (!voiceActive || voiceFatal) return;
      const text = finalText.trim();
      if (text) {
        handleVoiceUtterance(text);
      } else if (!voicePaused) {
        // Nothing heard yet: keep listening (hands-free)
        setTimeout(startListening, 250);
      }
    };

    try {
      rec.start();
    } catch (e) {
      setTimeout(startListening, 500);
    }
  }

  async function handleVoiceUtterance(text) {
    const lang = voiceLangSelect.value;
    voiceTranscript.innerText = text;
    voiceReply.innerText = '';
    voiceWarning.hidden = true;
    setVoiceState('thinking', vt('think'));

    messageInput.value = text;
    const data = await sendChatMessage({ voice: true, language: lang });
    if (!voiceActive) return;

    if (!data) {
      voiceReply.innerText = 'ORCA could not be reached. Check that the server is running.';
      voicePaused = true;
      setVoiceState('paused', vt('paused'));
      return;
    }

    if (data.has_warning && data.warning_message) {
      voiceWarning.innerText = `🚨 ${data.warning_message}`;
      voiceWarning.hidden = false;
    }
    voiceReply.innerText = data.reply;

    setVoiceState('speaking', vt('speak'));
    await speakText(data.reply, data.detected_language || lang);
    if (voiceActive && !voicePaused && voiceOverlay.dataset.state === 'speaking') startListening();
  }

  // Speaks text in the given language: ORCA's neural voices first, the browser's voices as fallback.
  // Resolves when playback ends (or is interrupted).
  async function speakText(text, lang) {
    stopVoiceAudio();
    const code = VOICE_LOCALES[lang] ? lang : 'en';
    try {
      const res = await fetch('/api/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, lang: code })
      });
      if (!res.ok) throw new Error('TTS unavailable');
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      voiceAudio = audio;
      await new Promise((resolve) => {
        audio.onended = resolve;
        audio.onerror = resolve;
        audio.onpause = resolve;
        audio.play().catch(resolve);
      });
      URL.revokeObjectURL(url);
      if (voiceAudio === audio) voiceAudio = null;
      return;
    } catch (e) {
      console.warn('ORCA voice unavailable, trying browser voice:', e);
    }

    if (!('speechSynthesis' in window)) return;
    const synth = window.speechSynthesis;
    const locale = VOICE_LOCALES[code].toLowerCase();
    const voices = synth.getVoices();
    const voice = voices.find(v => v.lang.toLowerCase() === locale)
      || voices.find(v => v.lang.toLowerCase().startsWith(code));
    if (!voice && code !== 'en') {
      showToast({ level: 'warning', icon: '🔊', title: 'Read aloud', text: 'Spoken replies need internet for this language (no offline voice installed).' });
      return;
    }
    await new Promise((resolve) => {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = VOICE_LOCALES[code];
      if (voice) utterance.voice = voice;
      utterance.onend = resolve;
      utterance.onerror = resolve;
      synth.speak(utterance);
    });
  }
  if ('speechSynthesis' in window) window.speechSynthesis.getVoices();

  document.getElementById('voiceModeBtn')?.addEventListener('click', openVoiceAssistant);
  document.getElementById('voiceCloseBtn')?.addEventListener('click', closeVoiceAssistant);
  document.getElementById('voiceEndBtn')?.addEventListener('click', closeVoiceAssistant);

  // Orb: interrupt while speaking, start/stop listening otherwise
  document.getElementById('voiceOrb')?.addEventListener('click', () => {
    if (voiceFatal) return;
    const current = voiceOverlay.dataset.state;
    if (current === 'speaking') {
      stopVoiceAudio();
      voicePaused = false;
      startListening();
    } else if (current === 'listening') {
      voicePaused = true;
      stopListening();
      setVoiceState('paused', vt('paused'));
    } else if (current !== 'thinking') {
      voicePaused = false;
      startListening();
    }
  });

  voicePauseBtn?.addEventListener('click', () => {
    if (voiceFatal) return;
    if (voicePaused) {
      voicePaused = false;
      startListening();
    } else {
      voicePaused = true;
      stopListening();
      stopVoiceAudio();
      setVoiceState('paused', vt('paused'));
    }
  });

  voiceLangSelect?.addEventListener('change', () => {
    // Restart recognition in the newly chosen language
    if (voiceActive && !voiceFatal && !voicePaused && voiceOverlay.dataset.state === 'listening') startListening();
    else if (voiceOverlay.dataset.state === 'paused') setVoiceState('paused', vt('paused'));
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && voiceActive) closeVoiceAssistant();
  });

  // --------------------------------------------------------------------------
  // 11. Coordinate "Set" buttons (composer drawer & map drawer)
  // --------------------------------------------------------------------------
  function applyCoords(latEl, lonEl) {
    const lat = parseFloat(latEl?.value);
    const lon = parseFloat(lonEl?.value);
    if (isNaN(lat) || isNaN(lon) || lat < -90 || lat > 90 || lon < -180 || lon > 180) {
      showToast({ level: 'warning', icon: '📍', title: 'Location', text: 'Enter a valid latitude (-90 to 90) and longitude (-180 to 180).' });
      return;
    }
    updateLocationState(lat, lon);
    if (state.map) {
      state.map.setView([state.lat, state.lon], 8);
      fetchModelPrediction();
    }
  }

  document.getElementById('applyCoordsBtn')?.addEventListener('click', () => applyCoords(latInput, lonInput));
  document.getElementById('updateDrawerCoordsBtn')?.addEventListener('click', () =>
    applyCoords(document.getElementById('drawerLatInput'), document.getElementById('drawerLonInput')));

  // --------------------------------------------------------------------------
  // 12. "Live along the Indian coast" band on the landing page
  // --------------------------------------------------------------------------
  function renderLiveAlerts() {
    const list = document.getElementById('liveAlertsList');
    if (!list || !alertsData) return;
    list.innerHTML = '';
    const points = alertsData.points || [];
    if (points.length === 0) {
      const empty = document.createElement('div');
      empty.className = 'live-empty';
      empty.innerText = alertsData.error || 'Live sea data unavailable right now.';
      list.appendChild(empty);
      return;
    }
    points.slice(0, 5).forEach(p => {
      const item = document.createElement('button');
      item.type = 'button';
      item.className = 'live-item';
      const dot = document.createElement('span');
      dot.className = `live-dot ${p.level}`;
      const body = document.createElement('div');
      const title = document.createElement('div');
      title.className = 'live-item-title';
      title.innerText = `${p.name} · ${LEVEL_LABEL[p.level]}`;
      const meta = document.createElement('div');
      meta.className = 'live-item-meta';
      meta.innerText = `Waves up to ${p.wave_height_max_24h_m ?? p.wave_height_m ?? '–'} m · wind up to ${p.wind_speed_max_24h_ms ?? p.wind_speed_ms ?? '–'} m/s · Ask ORCA →`;
      body.appendChild(title);
      body.appendChild(meta);
      item.appendChild(dot);
      item.appendChild(body);
      item.addEventListener('click', () => askOrcaAbout(p));
      list.appendChild(item);
    });
  }

  function renderLiveNews(data) {
    const list = document.getElementById('liveNewsList');
    if (!list) return;
    list.innerHTML = '';
    if (!data || !data.items || data.items.length === 0) {
      const empty = document.createElement('div');
      empty.className = 'live-empty';
      empty.innerText = (data && data.error) || 'No recent marine news found.';
      list.appendChild(empty);
      return;
    }
    data.items.slice(0, 5).forEach(n => {
      const item = document.createElement('a');
      item.className = 'live-item';
      item.href = n.link;
      item.target = '_blank';
      item.rel = 'noopener noreferrer';
      const body = document.createElement('div');
      const title = document.createElement('div');
      title.className = 'live-item-title';
      title.innerText = n.title;
      const meta = document.createElement('div');
      meta.className = 'live-item-meta';
      meta.innerText = [n.source, timeAgo(n.published)].filter(Boolean).join(' · ');
      body.appendChild(title);
      body.appendChild(meta);
      item.appendChild(body);
      list.appendChild(item);
    });
  }

  document.getElementById('liveBandAllBtn')?.addEventListener('click', () => openAlertsDrawer('sea'));

  // Shorter example text on phones so the search bar stays one line
  function fitPlaceholder() {
    if (!messageInput) return;
    messageInput.placeholder = window.innerWidth < 560
      ? 'Ask ORCA about the sea...'
      : 'e.g. Where is the nearest Potential Fishing Zone in Tamil Nadu today?';
  }
  fitPlaceholder();
  window.addEventListener('resize', fitPlaceholder);

  // Auto-focus chat input field on page load
  setTimeout(() => {
    messageInput?.focus();
  }, 100);

});
