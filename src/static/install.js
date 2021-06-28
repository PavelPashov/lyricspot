// Taken from https://www.flaskpwa.com/#_serviceWorkersInstallation
let deferredInstallPrompt = null;

window.addEventListener('beforeinstallprompt', saveBeforeInstallPromptEvent);

function saveBeforeInstallPromptEvent(evt) {
    deferredInstallPrompt = evt;
}

function installPWA(evt) {
    deferredInstallPrompt.prompt();
    $('#installButton').css('display', 'none');
    deferredInstallPrompt.userChoice
        .then((choice) => {
            if (choice.outcome === 'accepted') {
                console.log('User accepted the A2HS prompt', choice);

            } else {
                console.log('User dismissed the A2HS prompt', choice);
                $('#installButton').css('display', 'block')
            }
            deferredInstallPrompt = null;
        });
}
