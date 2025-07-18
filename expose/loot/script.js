var app = document.getElementById('app');

var typewriter = new Typewriter(app, {
  loop: true,
  delay: 50,
});

typewriter
  .pauseFor(1000)
  .typeString('Welcome to the ChatAI platform')
  .start();