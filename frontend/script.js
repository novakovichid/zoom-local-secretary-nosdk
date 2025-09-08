const statusEl = document.getElementById('status');
const transcriptEl = document.getElementById('transcript');
const summaryEl = document.getElementById('summary');

async function post(endpoint) {
  const res = await fetch(`http://localhost:8000/${endpoint}`, { method: 'POST' });
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
  summaryEl.textContent = '';
  try {
    const data = await post('transcribe_and_summarize');
    const [tResp, sResp] = await Promise.all([
      fetch(`http://localhost:8000/${data.transcript_path}`),
      fetch(`http://localhost:8000/${data.summary_path}`)
    ]);
    transcriptEl.textContent = await tResp.text();
    summaryEl.textContent = await sResp.text();
    statusEl.textContent = 'Done';
  } catch (err) {
    statusEl.textContent = err.message;
  }
};
