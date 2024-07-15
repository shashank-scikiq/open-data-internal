export const OverallStateOrderDataChartConfig = {
    colors: ["#00b8d4"],
    markers: { size: 3, strokeWidth: 2 },
    chart: {
        height: 180,
        width: "100%",
        type: 'area',
        stacked: false,
        toolbar: {
            show: false,
            tools: {
                download: false
            }
        }
    },
    stroke: {
        show: true,
        curve: 'smooth',
        width: [3, 3, 3, 0],
    },
    tooltip: {
        show: true,
        y: {
            formatter: function (val: any) {
                return val;
            },
            title: {
                formatter: (seriesName: any) => seriesName,
            },
        },
    },
    yaxis: {
        labels: {
          show: true,
          maxWidth: "auto",
          offsetX: -15,
        },
      }
}