const statusEl = document.getElementById('status');
const transcriptEl = document.getElementById('transcript');
const fileInput = document.getElementById('file');

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
  try {
    const data = await post('transcribe');
    const tResp = await fetch(`http://localhost:8000/${data.transcript_path}`);
    transcriptEl.textContent = await tResp.text();
    statusEl.textContent = 'Done';
  } catch (err) {
    statusEl.textContent = err.message;
  }
};

document.getElementById('run-file').onclick = async () => {
  if (!fileInput.files.length) {
    statusEl.textContent = 'Please select a file';
    return;
  }
  statusEl.textContent = 'Processing…';
  transcriptEl.textContent = '';
  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  try {
    const res = await fetch('http://localhost:8000/transcribe_file', {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      throw new Error((await res.text()) || res.statusText);
    }
    const data = await res.json();
    const tResp = await fetch(`http://localhost:8000/${data.transcript_path}`);
    transcriptEl.textContent = await tResp.text();
    statusEl.textContent = 'Done';
  } catch (err) {
    statusEl.textContent = err.message;
  }
};
