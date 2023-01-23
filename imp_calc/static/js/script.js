function idleTimer() {
    var t;
    //window.onload = resetTimer;
    window.onmousemove = resetTimer; // catches mouse movements
    window.onmousedown = resetTimer; // catches mouse movements
    window.onclick = resetTimer;     // catches mouse clicks
    window.onscroll = resetTimer;    // catches scrolling
    window.onkeypress = resetTimer;  //catches keyboard actions

    function logout() {
        window.location.href = '/logout';  //Adapt to actual logout script
    }

   function reload() {
          window.location = self.location.href;  //Reloads the current page
   }

   function resetTimer() {
        clearTimeout(t);
        t = setTimeout(logout, 180000);  // time is in milliseconds (1000 is 1 second)
        t= setTimeout(reload, 30000);  // time is in milliseconds (1000 is 1 second)
    }
}
var navItems = document.querySelectorAll(".nav-item");
for (var i = 0; i < navItems.length; i++) {
   navItems[i].addEventListener("click", function() {
      this.classList.add("active");
   });
}
idleTimer();


function print_current_page()
{
window.print();
}

// // Set timeout variables.
// var timoutWarning = 10; // Display warning in 14 Mins.
// var timoutNow = 30; // Warning has been shown, give the user 1 minute to interact
// var logoutUrl = '/logout'; // URL to logout page.

// var warningTimer;
// var timeoutTimer;

// // Start warning timer.
// function StartWarningTimer() {
//     warningTimer = setTimeout("IdleWarning()", timoutWarning);
// }

// // Reset timers.
// function ResetTimeOutTimer() {
//     clearTimeout(timeoutTimer);
//     StartWarningTimer();
//     $("#timeout").dialog('close');
// }

// // Show idle timeout warning dialog.
// function IdleWarning() {
//     clearTimeout(warningTimer);
//     timeoutTimer = setTimeout("IdleTimeout()", timoutNow);
//     $("#timeout").dialog({
//         modal: true
//     });
//     // Add code in the #timeout element to call ResetTimeOutTimer() if
//     // the "Stay Logged In" button is clicked
// }

// // Logout the user.
// function IdleTimeout() {
//     window.location = logoutUrl;
// }