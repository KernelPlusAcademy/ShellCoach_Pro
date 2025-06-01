const term = new Terminal({
  convertEol: true,
  cursorBlink: true,
  fontFamily: 'monospace',
  fontSize: 14,
  theme: {
    background: '#000000',
    foreground: '#ffffff'
  }
});
term.open(document.getElementById('terminal'));
term.write('Welcome to ShellCoach\r\n$ ');

let buffer = '';

function printPrompt() {
  term.write('\r\n$ ');
}

term.onKey(e => {
  const key = e.key;

  if (key === '\r') {
    const command = buffer.trim();

    // Print the command the user typed (optional for visual echo)
    term.write('\r\n');

    fetch('/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command: command })
    })
    .then(res => res.json())
    .then(data => {
      term.write(data.output.replace(/\n/g, '\r\n'));

      // If AI toggle is on, explain
      if (document.getElementById('ai-toggle').checked) {
        fetch('/explain', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ command: command })
        })
        .then(res => res.json())
        .then(ai => {
          term.write(`\r\n\x1b[36m[AI Explanation]\x1b[0m ${ai.explanation.replace(/\n/g, '\r\n')}`);
          printPrompt();
        });
      } else {
        printPrompt();
      }
    });

    buffer = '';
  } else if (key === '\u007f') { // backspace
    if (buffer.length > 0) {
      buffer = buffer.slice(0, -1);
      term.write('\b \b');
    }
  } else {
    buffer += key;
    term.write(key);
  }
});
