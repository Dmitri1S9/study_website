document.addEventListener('DOMContentLoaded', function() {
  const registerButtons = document.querySelectorAll('.register-btn');
  const loginContainer = document.getElementById('login-container');
  const welcomeContainer = document.getElementById('welcome-container');
  const usernameGroupContainer = document.getElementById('username_group');
  const usernameInput = document.querySelector('#username');
  const emailInput = document.querySelector('#email');
  const passwordInput = document.querySelector('#password');
  const loginFlag = document.getElementById('flag');
  const container = document.querySelector('#vjiro');
  const changeModeButton = document.querySelector('#change-mode-to-login');

  let flag = true;

  function swapContainers() {
    const isLoginMode = flag;

    loginContainer.classList.add(isLoginMode ? 'swap-back' : 'swap');
    welcomeContainer.classList.add(isLoginMode ? 'swap' : 'swap-back');

    container.style.flexDirection = isLoginMode ? 'row-reverse' : 'row';
    changeModeButton.textContent = isLoginMode ? 'LOGIN' : 'REGISTRATION';
    usernameGroupContainer.style.display = isLoginMode ? 'none' : 'flex';
    loginFlag.value = isLoginMode ? 'true' : 'false';

    flag = !isLoginMode;

    setTimeout(() => {
      loginContainer.classList.remove('swap', 'swap-back');
      welcomeContainer.classList.remove('swap', 'swap-back');
    }, 500);
  }

  changeModeButton.addEventListener('click', function(event) {
    event.preventDefault();
    swapContainers();
  });

  registerButtons.forEach(button => {
    button.addEventListener('mouseover', () => {
      button.style.boxShadow = '0 0 10px 5px #2e4d3c';
    });

    button.addEventListener('mouseout', () => {
      button.style.boxShadow = 'none';
    });
  });

  const forms = document.querySelectorAll('.registration-form');
  forms.forEach(form => {
    form.addEventListener('submit', function(event) {
      const username = usernameInput.value.trim();
      const email = emailInput.value.trim();
      const password = passwordInput.value.trim();

      // if (username.length < 3) {
      //   alert('Ваше имя должно содержать не менее 3 символов, молодой маг!');
      //   event.preventDefault();
      //   return;
      // }
      //
      // const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      // if (!emailPattern.test(email)) {
      //   alert('Пожалуйста, введите корректный email.');
      //   event.preventDefault();
      //   return;
      // }
      //
      // if (password.length < 6) {
      //   alert('Пароль должен содержать не менее 6 символов.');
      //   event.preventDefault();
      //   return;
      // }
    });
  });
});
