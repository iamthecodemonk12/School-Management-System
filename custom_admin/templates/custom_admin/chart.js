"use strict";
$(function () {
  chart7();
});

function chart7() {
  var options = {
    chart: {
      width: 360,
      type: "pie",
    },
    labels: ["Students Processed", "Students Not Processed", "Students Partially Processed"],
    series: [44, 55, 13, ],
    responsive: [
      {
        breakpoint: 480,
        options: {
          chart: {
            width: 360,
          },
          legend: {
            position: "bottom",
          },
        },
      },
    ],
  };

  var chart = new ApexCharts(document.querySelector("#chart7"), options);

  chart.render();
}