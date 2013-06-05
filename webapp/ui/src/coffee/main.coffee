
#

testing = true

print = (stuff...) ->
    console.log.apply(console, stuff)

Date::getUnixEpoch = ->
    return +this / 1000

Charts = 
    dates:
        week: ->
            if testing
                start = Date.parse("2013-05-19")
                return [start.getUnixEpoch(), start.add(7).days().getUnixEpoch()]
            [(7).days().ago().getUnixEpoch(), Date.today().getUnixEpoch()]
        
        spark: ->
            if testing
                start = Date.parse("2013-05-26 11:00")
                return [start.getUnixEpoch(), start.add(2).hours().getUnixEpoch()]
            [(2).hours().ago().getUnixEpoch(), Date.today().getUnixEpoch()]

    filter:
        filter: (data, col) ->
            points = []
            for row in data
                points.push
                    x: row[4]
                    y: row[col]
            return points

        sum: (data) ->
            return Charts.filter.filter data, 3
        
        avg: (data) ->
            return Charts.filter.filter data, 0

    render:
        spark: (data, element) ->
            nv.addGraph
                generate: ->
                    chart = nv.models.sparkline().width(100).height(50)
                    d3.select(element).datum(data).call(chart)
                    chart
        
        line: (data, element) ->
            nv.addGraph
                generate: ->
                    chart = nv.models.lineChart()
                        .width(280)
                        .height(160)
                        .showLegend(false)
                    chart.xAxis
                        .ticks(8)
                        .tickFormat((ut) -> d3.time.format("%m-%d %H:%M")(new Date(ut * 1000)))
                    chart.yAxis
                        .ticks(4)
                        .tickFormat(d3.format('.0f'))
                    
                    d3
                        .select(element)
                        .datum(data)
                        .transition()
                        .duration(500)
                        .call(chart)
                    
                    chart


class InfoPod
    constructor: (@sensor) ->
        @jq = $('#' + @sensor.short)
        @interval = null
        @update()
        @start()

    display: (value) ->
        @jq.find('.value').html value

    update: =>
        $.getJSON "/data/current/#{@sensor.id}", (data) =>
            if data and data.value
                InfoPod.lastUpdated = data.unix_epoch
                @display data.value

    stop: ->
        clearInterval @interval

    start: ->
        @interval = setInterval @update, 30000


    sparkline: =>
        [start, end] = Charts.dates.spark()
        $.getJSON "/data/recent/#{@sensor.id}/#{start}/#{end}", (data) =>
            points = []
            for row in data.data
                point =
                    y: row[1]
                    x: new Date(row[0] * 1000) #tm.getHours() + ':' + tm.getMinutes()
                points.push point
            Charts.render.spark points, @jq.find('.sparkline').get(0)

    chart: =>
        [start, end] = Charts.dates.week()
        $.getJSON "/data/hourly/#{@sensor.id}/#{start}/#{end}", (data) =>
            results = [
                values: Charts.filter.avg data.data
                key: @sensor.short
                color: '#F1601D'
            ]
            Charts.render.line results, @jq.find('.chart').get(0)
    
    @lastUpdated = 0

    @create: (sensor) ->
        switch sensor.short
            when "Pumping" then new PumpingInfoPod(sensor)
            when "Water" then new WaterInfoPod(sensor)
            when "Temperature", "Humidity", "Moisture" then new TrendingInfoPod(sensor)
            else new InfoPod(sensor)

class PumpingInfoPod extends InfoPod
    display: (value) ->
        if value == 1
            @jq
                .find('i').addClass('icon-play') 
                .find('span').html('Pump is running')

        else
            @jq
                .find('i').addClass('icon-stop')
                .find('span').html('Pump is stopped')

        @chart()

    chart: =>
        [start, end] = Charts.dates.week()
        $.getJSON "/data/daily/#{@sensor.id}/#{start}/#{end}", (data) =>
            results = [
                values: Charts.filter.sum data.data
                key: @sensor.short
                color: '#17A768'
            ]
            Charts.render.line results, @jq.parents('.info').find('.chart').get(0)


class WaterInfoPod extends InfoPod
    display: (value) ->
        if value == 1
            @jq
                .find('i').addClass('icon-warning-sign')
                .find('span').html('Not enough water!')
        else
            @jq
                .find('i').addClass('icon-ok')
                .find('span').html('Plenty of water')


class TrendingInfoPod extends InfoPod
    display: (value) ->
        super value
        @sparkline()
        @chart()
    
class SmallInfoPod extends InfoPod
    

pods = []

$ ->
    
    for sensor in sensors
        pods[sensor.id] = InfoPod.create(sensor)

