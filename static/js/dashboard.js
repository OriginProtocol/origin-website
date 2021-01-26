(function () {

  var releaseScheduleXAxes = [
    'Jan 2020', 'Feb 2020', 'Mar 2020', 'Apr 2020', 'May 2020', 'Jun 2020', 'Jul 2020', 'Aug 2020', 'Sep 2020', 'Oct 2020', 'Nov 2020', 'Dec 2020', 
    'Jan 2021', 'Feb 2021', 'Mar 2021', 'Apr 2021', 'May 2021', 'Jun 2021', 'Jul 2021', 'Aug 2021', 'Sep 2021', 'Oct 2021', 'Nov 2021', 'Dec 2021', 
    'Jan 2022', 'Feb 2022', 'Mar 2022', 'Apr 2022', 'May 2022', 'Jun 2022', 'Jul 2022', 'Aug 2022', 'Sep 2022', 'Oct 2022', 'Nov 2022', 'Dec 2022', 
    'Jan 2023', 'Feb 2023', 'Mar 2023', 'Apr 2023', 'May 2023', 'Jun 2023', 'Jul 2023', 'Aug 2023', 'Sep 2023', 'Oct 2023', 'Nov 2023', 'Dec 2023', 
    'Jan 2024', 'Feb 2024', 'Mar 2024', 'Apr 2024', 'May 2024', 'Jun 2024', 'Jul 2024'
  ]

  var releaseScheduleData = {
    partnerships: [0.04,0.04,0.04,0.04,0.13,0.13,0.13,0.22,0.22,0.22,0.3,0.3,0.3,0.39,0.39,0.39,0.47,0.47,0.47,0.56,0.56,0.56,0.65,0.65,0.65,0.73,0.73,0.73,0.73,0.73,0.73,0.73,0.73,0.73,0.73,0.73,0.73,0.73,0.73,0.73,0.73,0.73,0.73,0.73,0.73,0.73,0.73,0.73,0.73,0.73,0.73,0.73,0.73,0.73,0.73],
    coinlist_round: [0.29,0.29,0.29,0.29,0.86,0.86,0.86,1.43,1.43,1.43,2,2,2,2.57,2.57,2.57,3.13,3.13,3.13,3.7,3.7,3.7,4.27,4.27,4.27,4.84,4.84,4.84,4.84,4.84,4.84,4.84,4.84,4.84,4.84,4.84,4.84,4.84,4.84,4.84,4.84,4.84,4.84,4.84,4.84,4.84,4.84,4.84,4.84,4.84,4.84,4.84,4.84,4.84,4.84],
    strategic_round: [1.43,1.43,1.43,1.43,4.22,4.22,4.22,7.01,7.01,7.01,9.8,9.8,9.8,12.59,12.59,12.59,15.38,15.38,15.38,18.17,18.17,18.17,20.96,20.96,20.96,23.75,23.75,23.75,23.75,23.75,23.75,23.75,23.75,23.75,23.75,23.75,23.75,23.75,23.75,23.75,23.75,23.75,23.75,23.75,23.75,23.75,23.75,23.75,23.75,23.75,23.75,23.75,23.75,23.75,23.75],
    advisor_sale: [0.26,0.26,0.26,0.26,0.78,0.78,0.78,1.29,1.29,1.29,1.81,1.81,1.81,2.32,2.32,2.32,2.84,2.84,2.84,3.35,3.35,3.35,3.87,3.87,3.87,4.38,4.38,4.38,4.38,4.38,4.38,4.38,4.38,4.38,4.38,4.38,4.38,4.38,4.38,4.38,4.38,4.38,4.38,4.38,4.38,4.38,4.38,4.38,4.38,4.38,4.38,4.38,4.38,4.38,4.38],
    advisor_grants: [0,0,0,0.17,0.31,0.45,0.58,0.72,0.86,1,1.14,1.27,1.41,1.55,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69,1.69],
    team: [0,0,0,1.05,1.11,2.85,3.4,3.5,3.61,3.71,3.82,5.59,5.69,5.79,5.9,6,6.11,7.88,7.98,8.09,8.19,8.29,8.4,10.17,10.27,10.37,10.48,10.58,10.67,12.43,12.52,12.6,12.68,12.77,12.85,14.59,14.66,14.74,14.81,14.88,14.95,16.69,16.76,16.79,16.82,16.85,16.88,18.58,18.58,18.58,18.58,18.58,18.58,20.24,20.24],
    ecosystem_growth: [0.05,0.1,0.15,0.21,0.27,0.33,0.39,0.46,0.53,0.6,0.68,0.76,0.85,0.94,1.03,1.13,1.23,1.34,1.46,1.58,1.7,1.84,1.98,2.12,2.28,2.44,2.61,2.78,2.97,3.17,3.37,3.59,3.81,4.05,4.3,4.57,4.84,5.13,5.44,5.75,6.09,6.44,6.81,7.2,7.61,8.04,8.48,8.96,9.45,9.97,10.52,11.09,11.69,12.32,12.99],
    foundation_reserves: [0.31,0.31,0.31,0.78,0.78,0.78,1.41,1.41,1.41,2.04,2.04,2.04,2.67,2.67,2.67,3.29,3.29,3.29,3.92,3.92,3.92,4.55,4.55,4.55,5.18,5.18,5.18,5.8,5.8,5.8,6.43,6.43,6.43,7.06,7.06,7.06,7.69,7.69,7.69,8.31,8.31,8.31,8.94,8.94,8.94,9.57,9.57,9.57,10.2,10.2,10.2,10.82,10.82,10.82,11.45]
  }

  var monthToModeledValue = {}
  Object.values(releaseScheduleXAxes)
    .map((month, index) => {
      var val = Object.keys(releaseScheduleData)
        .map(k => releaseScheduleData[k][index])
        .reduce((sum, v) => sum + v, 0)
      
      monthToModeledValue[month] = parseInt((10000000 * val) / 1000000)
    })

  function formattedDate(dateObj) {
    var currentMonth = dateObj.getMonth()

    var monthName = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][currentMonth]
    return monthName + ' ' + dateObj.getFullYear()
  }
  function initUnlockChart(canvasEl, legendsEl) {
    var datasets = { 
      partnerships: {
        borderColor: '#1a82ff',
        label: 'Long-term Partnership',
      },
      coinlist_round: {
        borderColor: '#7a54ef',
        label: 'CoinList Round',
      },
      strategic_round: {
        borderColor: '#00d592',
        label: 'Strategic Round',
      },
      advisor_sale: {
        borderColor: '#fec100',
        label: 'Advisor Sale',
      },
      advisor_grants: {
        borderColor: '#2e3f53',
        label: 'Advisor Grants',
      },
      team: {
        borderColor: '#111d28',
        label: 'Team',
      },
      ecosystem_growth: {
        borderColor: '#ed2a28',
        label: 'Ecosystem Growth',
      },
      foundation_reserves: {
        borderColor: '#007246',
        label: 'Foundation Reserves',
      },
    }

    var cdata = {
      type: 'line', 
      data: { 
        labels: releaseScheduleXAxes, 
        datasets: Object.keys(datasets)
          .map(k => ({
            ...datasets[k],
            data: releaseScheduleData[k],
            // fill: 'origin',
            fill: false,
            pointHoverRadius: 1,
            pointRadius: 1,
            borderSize: 0.2
          }))
      }, 
      options: { 
        maintainAspectRatio: false, 
        spanGaps: false, 
        elements: { 
          line: { 
            tension: 0.000001 
          } 
        }, 
        plugins: { 
          filler: { 
            propagate: false 
          } 
        }, 
        scales: { 
          xAxes: [{ 
            ticks: { 
              display: true,
              max: 2
            } 
          }],
          yAxes: [{
            ticks: {
              min: 0,
              stepSize: 25,
              callback: function(value, index, values) {
                return value + '%'
              }
            },
            stacked: true
          }]
        }, 
        title: { 
          text: 'Token Schedule', 
          display: false 
        },
        legend: {
          display: false,
          position: 'bottom'
        },
        legendCallback: function (chart) {
          var text = []
          text.push('<div class="' + chart.id + '-legend chart-legends grid-type">')  
          for (var i = 0; i < chart.data.datasets.length; i++) {
            text.push('<div class="legend-item">')
            text.push('<span class="legend-color" style="background-color:' + chart.data.datasets[i].borderColor + '"></span>')
            text.push('<span class="legend-name">' + chart.data.datasets[i].label + '</span>')
            text.push('</div>')
          }
          text.push('</div>')
          return text.join('')
        },
        tooltips: {
          mode: 'index',
          intersect: false,
          callbacks: {
            label: function (d) { return d.value + '%' }
          }
        }
      } 
    }

    var chartObj = new Chart(canvasEl, cdata)
    
    if (legendsEl) {
      legendsEl.innerHTML = chartObj.generateLegend()
    }
  }

  function initReleaseChart(canvasEl, legendsEl) {
    var ognSupplyHistory = window.ognSupplyHistory || []
    var dataLen = ognSupplyHistory.length

    var xAxesLabels = ognSupplyHistory.map(x => new Date(x.snapshot_date))

    var releasedData = ognSupplyHistory.map(x => parseInt(x.supply_amount / 1000000))

    var modeledData = new Array(dataLen).fill(0)
      .map((_, index) => {
        var d = formattedDate(new Date(ognSupplyHistory[index].snapshot_date))
        return monthToModeledValue[d]
      })

    var maxVal = Math.ceil(Math.max(modeledData[0], releasedData[0]) / 100) * 100 + 100

    var datasets = {
      modeled: {
        borderColor: '#1a82ff',
        label: 'Modeled',
        data: modeledData
      },
      released: {
        borderColor: '#7a54ef',
        label: 'Actual',
        data: releasedData
      },
    }

    var cdata = {
      type: 'line', 
      data: { 
        labels: xAxesLabels.slice(0, ognSupplyHistory.length), 
        datasets: Object.keys(datasets)
          .map(k => ({
            ...datasets[k],
            // fill: 'origin',
            fill: false,
            pointHoverRadius: 1,
            pointRadius: 1,
            borderSize: 0.2
          }))
      }, 
      options: { 
        maintainAspectRatio: false, 
        spanGaps: false, 
        elements: { 
          line: { 
            tension: 0.000001 
          } 
        }, 
        plugins: { 
          filler: { 
            propagate: false 
          } 
        }, 
        scales: { 
          xAxes: [{ 
            type: 'time',
            time: {
              displayFormats: {
                quarter: 'MMM YYYY'
              },
              minUnit: 'month'
            },
            ticks: { 
              display: true
            } 
          }],
          yAxes: [{
            ticks: {
              min: 0,
              stepSize: maxVal / 4,
              max: maxVal,
              callback: function(value, index, values) {
                return value + 'M'
              }
            },
            stacked: false
          }]
        }, 
        title: { 
          text: 'Token Schedule', 
          display: false 
        },
        legend: {
          display: false,
          position: 'bottom'
        },
        legendCallback: function (chart) {
          var text = []
          text.push('<div class="' + chart.id + '-legend chart-legends">')  
          for (var i = 0; i < chart.data.datasets.length; i++) {
            text.push('<div class="legend-item">')
            text.push('<span class="legend-color" style="background-color:' + chart.data.datasets[i].borderColor + '"></span>')
            text.push('<span class="legend-name">' + chart.data.datasets[i].label + '</span>')
            text.push('</div>')
          }
          text.push('</div>')
          return text.join('')
        },
        tooltips: {
          mode: 'index',
          intersect: false,
          callbacks: {
            label: function (d) { return d.value + 'M' }
          }
        }
      }
    }

    var chartObj = new Chart(canvasEl, cdata)
    
    if (legendsEl) {
      legendsEl.innerHTML = chartObj.generateLegend()
    }
  }

  function transformStakedStats(data) {
    const total = data.reduce((stored, current, index) => index == 1 ? Number(stored[1]) : Number(stored) + Number(current[1]));
    const getPercentage = (value) => parseInt(Number(value)/total * 100)
    return data.map(each => ({
      title: `${each[0]} days - ${getPercentage(each[1])}%`,
      value: parseInt(each[1]),
      value_human: `${parseInt(each[1]).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")} OGN`,
    }))
  }

  function initStakedAmountChart(canvasEl, legendsEl) {
    var data = transformStakedStats(window.ognStakedStats || [])
    var cdata = {
      type: 'doughnut', 
      data: {
        labels: data.map(each => `${each.title} (${each.value_human})`),
        datasets: [{
          label: 'Staked amount by duration',
          data: data.map(each => each.value),
          backgroundColor: ['#007cff', '#00d592', '#7b52ef'],
          borderWidth: 1
        }]
      },
      options: { 
        maintainAspectRatio: false, 
        spanGaps: false, 
        cutoutPercentage: 80,
        rotation: 70,
        title: { 
          text: 'Staked amount', 
          display: false 
        },
        legend: {
          display: false
        },
        legendCallback: function (chart) {
          var text = []
          text.push('<div class="' + chart.id + '-legend chart-legends grid-type d-flex flex-column mt-md-0">')  
          for (var i = 0; i < chart.data.labels.length; i++) {
            text.push('<div class="legend-item mt-2 mb-2">')
            text.push('<span class="legend-color legend-small" style="background-color:' + chart.data.datasets[0].backgroundColor[i] + '"></span>')
            text.push('<span class="legend-name font-weight-normal">' + chart.data.labels[i] + '</span>')
            text.push('</div>')
          }
          text.push('</div>')
          return text.join('')
        },
        tooltips: {
          callbacks: {
            label: function (d) { return data[d.index].value_human }
          }
        }
      } 
    }

    var chartObj = new Chart(canvasEl, cdata)
    
    if (legendsEl) {
      legendsEl.innerHTML = chartObj.generateLegend()
    }
  }

  function updateDynamicValues() {
    var modeledSupply = monthToModeledValue[formattedDate(new Date())] * 1000000
    var currentSupply = window.ognSupplyHistory[0].supply_amount
    var supplyDiff = modeledSupply - currentSupply
    var diffInPct = parseInt(100 * (1 - (currentSupply / modeledSupply)))
    var el = document.getElementById('supplyDataEl')

    el.innerText = el.innerText
      .replace('ogn_modeled_supply', modeledSupply.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ','))
      .replace('ogn_supply_diff_pct', diffInPct)
      .replace('ogn_supply_diff', supplyDiff.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ','))
      .replace('ogn_circulating_supply', currentSupply.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ','))
  }

  function onDOMReady() {
    var unlockChart = document.getElementById('unlock_schedule_chart')
    var releaseChart = document.getElementById('release_schedule_chart')
    var stakedAmountChart = document.getElementById('staked_amount_chart')

    var unlockLegends = document.getElementById('unlock_schedule_legends')
    var releaseLegends = document.getElementById('release_schedule_legends')
    var stakedAmountLegends = document.getElementById('staked_amount_legends')

    if (!unlockChart || !releaseChart || !stakedAmountChart) return

    initUnlockChart(unlockChart, unlockLegends)
    initReleaseChart(releaseChart, releaseLegends)
    initStakedAmountChart(stakedAmountChart, stakedAmountLegends)
    updateDynamicValues()
  }

  document.addEventListener('DOMContentLoaded', onDOMReady)
})()
