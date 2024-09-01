$(document).ready(function () {

//Show Password Login
  $(".eyeIcon").click(function () {
    if($(this).hasClass("fa-eye-slash")) {
      $(this).removeClass("fa-eye-slash");
      $(this).addClass("fa-eye");
      $("#password").attr("type", "text");
    } else {
      $(this).addClass("fa-eye-slash");
      $(this).removeClass("fa-eye");
      $("#password").attr("type", "password");
    }
  });

  // job seeker Registration;
  $("#nextProfession").click(function () {
    $(".professionalLevelPage").removeClass("hidden");
    $(".professionPage").addClass("hidden");
  });
  $("#backProfession").click(function () {
    $(".professionalLevelPage").addClass("hidden");
    $(".professionPage").removeClass("hidden");
  });
  $("#nextProfessional").click(function () {
    $(".professionalLevelPage").addClass("hidden");
    $(".skillsPage").removeClass("hidden");
  });
  $("#backProfessional").click(function () {
    $(".professionalLevelPage").removeClass("hidden");
    $(".skillsPage").addClass("hidden");
  });
  $("#nextSkills").click(function () {
    $(".skillsPage").addClass("hidden");
    $(".personalPage").removeClass("hidden");
    $("#mextPersonal").removeClass("disabled");
  });
    $("#backSkills").click(function () {
    $(".personalPage").addClass("hidden");
    $(".skillsPage").removeClass("hidden");
  });
  $("#backProfessional").click(function () {
    $(".professionalLevelPage").removeClass("hidden");
    $(".personalPage").addClass("hidden");
  });
  $("#nextPersonal").click(function (e) {
    $(".personalPage").addClass("hidden");
    $(".loginPage").removeClass("hidden");
  });
  $("#backPersonal").click(function (e) {
    $(".personalPage").removeClass("hidden");
    $(".loginPage").addClass("hidden");
  });


  //bookmark icon
  function bookmark(){
      var bmIcon = $(this).hasClass("fa-solid");
      if (bmIcon === true) {
        $(this).removeClass("fa-solid");
        $(this).addClass("fa-regular");
      } else {
        $(this).addClass("fa-solid");
        $(this).removeClass("fa-regular");
      }
  }

  // Apply for job
  $("#attest").click(function () {
    var attest = $("#attest").prop("checked");
    var motivation = $("#motivation").val();
    if (attest === true && motivation) {
      $(".sign").removeClass("hidden");
    } else {
      $(".sign").addClass("hidden");
    }
  });
});

// Modal

