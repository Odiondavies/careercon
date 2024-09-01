$(document).ready(function () {
  $("#changePassword").click(function () {
    $(".changePassword").removeClass("hidden");
    $(".admin").removeClass("hidden");
    $("#changePassword").addClass("active");
    $(".manageAdmin, .addAdmin, .employers, .jobSeekers,.settings").addClass(
      "hidden"
    );
    $(
      "#addAdmin, #manageAdmin, #manageEmployers, #manageJobSeekers, #adminSettings"
    ).removeClass("active");
  });
  $("#addAdmin").click(function () {
    $(".addAdmin").removeClass("hidden");
    $(".admin").removeClass("hidden");
    $("#addAdmin").addClass("active");
    $(
      ".changePassword, .manageAdmin, .employers, .jobSeekers, .settings"
    ).addClass("hidden");
    $(
      "#changePassword, #manageAdmin, #manageEmployers, #manageJobSeekers, #adminSettings"
    ).removeClass("active");
  });
  $("#manageAdmin").click(function () {
    $(".manageAdmin").removeClass("hidden");
    $(".admin").removeClass("hidden");
    $("manageAdmin").addClass("active");
    $("#manageAdmin").addClass("active");
    $(
      ".changePassword, .addAdmin, .employers, .jobSeekers, .settings"
    ).addClass("hidden");
    $(
      "#changePassword, #addAdmin, #manageEmployers, #manageJobSeekers, #adminSettings"
    ).removeClass("active");
  });
  $("#manageEmployers").click(function () {
    $(".employers").removeClass("hidden");
    $(".admin, .jobSeekers, .settings").addClass("hidden");
    $("#manageEmployers").addClass("active");
    $(
      "#changePassword, #addAdmin, #manageAdmin, #manageJobSeekers, #adminSettings"
    ).removeClass("active");
  });
  $("#manageJobSeekers").click(function () {
    $(".jobSeekers").removeClass("hidden");
    $(".admin, .employers, .settings").addClass("hidden");
    $("#manageJobSeekers").addClass("active");
    $(
      "#changePassword, #addAdmin, #manageAdmin, #manageEmployers, #adminSettings"
    ).removeClass("active");
  });
  $("#adminSettings").click(function () {
    $(".settings").removeClass("hidden");
    $(".admin, .jobSeekers, .employers").addClass("hidden");
    $("#adminSettings").addClass("active");
    $(
      "#changePassword, #addAdmin, #manageAdmin, #manageEmployers, #manageJobSeekers"
    ).removeClass("active");
  });
  $("#editName").click(function () {
    var name = $(".name").text();
    $(".updateName").removeClass("hidden");
    $("#updateName").val(name);
    $(".updateEmail").addClass("hidden");
  });
  $("#editEmail").click(function () {
    var email = $(".email").text();
    $(".updateName").addClass("hidden");
    $("#updateEmail").val(email);
    $(".updateEmail").removeClass("hidden");
  });
});
