var navItems = document.querySelectorAll(".nav-item");
for (var i = 0; i < navItems.length; i++) {
   navItems[i].addEventListener("click", function() {
      this.classList.add("active");
      });
   }