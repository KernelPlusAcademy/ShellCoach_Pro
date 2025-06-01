
const term = new Terminal();
term.open(document.getElementById('terminal'));
term.write('Welcome to ShellCoach\r\n$ ');

let buffer = '';

term.onKey(e => {
  const key = e.key;

  if (key === '\r') {
    const command = buffer.trim();
    fetch('/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command: command })
    })
    .then(res => res.json())
    .then(data => {
      term.write('\r\n' + data.output);
      const aiToggle = document.getElementById('ai-toggle');
      if (aiToggle.checked) {
        fetch('/explain', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ command: command })
        })
        .then(res => res.json())
        .then(ai => {
          term.write('\r\n\x1b[36m[AI Explanation]\x1b[0m ' + ai.explanation);
          term.write('\r\n$ ');
        });
      } else {
        term.write('\r\n$ ');
      }
    });
    buffer = '';
  } else if (key === '\u007f') {
    if (buffer.length > 0) {
      buffer = buffer.slice(0, -1);
      term.write('\b \b');
    }
  } else {
    buffer += key;
    term.write(key);
  }
});
