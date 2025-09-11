const statusEl = document.getElementById('status');
const transcriptEl = document.getElementById('transcript');

async function post(endpoint) {
  const res = await fetch(`/api/${endpoint}`, { method: 'POST' });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json();
}

document.getElementById('start').onclick = async () => {
  statusEl.textContent = 'Starting…';
  try {
    const data = await post('start_recording');
    statusEl.textContent = data.status;
  } catch (err) {
    statusEl.textContent = err.message;
  }
};

document.getElementById('stop').onclick = async () => {
  statusEl.textContent = 'Stopping…';
  try {
    const data = await post('stop_recording');
    statusEl.textContent = `${data.status}: ${data.audio_path}`;
  } catch (err) {
    statusEl.textContent = err.message;
  }
};

document.getElementById('run').onclick = async () => {
  statusEl.textContent = 'Processing…';
  transcriptEl.textContent = '';
  try {
    const data = await post('transcribe');
    const tResp = await fetch(`/${data.transcript_path}`);
    transcriptEl.textContent = await tResp.text();
    statusEl.textContent = 'Done';
  } catch (err) {
    statusEl.textContent = err.message;
  }
};
