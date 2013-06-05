(function() {
  var Charts, InfoPod, PumpingInfoPod, SmallInfoPod, TrendingInfoPod, WaterInfoPod, pods, print, sensors, testing, _ref, _ref1, _ref2, _ref3,
    __slice = [].slice,
    __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
    __hasProp = {}.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

  testing = true;

  print = function() {
    var stuff;

    stuff = 1 <= arguments.length ? __slice.call(arguments, 0) : [];
    return console.log.apply(console, stuff);
  };

  Date.prototype.getUnixEpoch = function() {
    return +this / 1000;
  };

  Charts = {
    dates: {
      week: function() {
        var start;

        if (testing) {
          start = Date.parse("2013-05-19");
          return [start.getUnixEpoch(), start.add(7).days().getUnixEpoch()];
        }
        return [7..days().ago().getUnixEpoch(), Date.today().getUnixEpoch()];
      },
      spark: function() {
        var start;

        if (testing) {
          start = Date.parse("2013-05-26 11:00");
          return [start.getUnixEpoch(), start.add(2).hours().getUnixEpoch()];
        }
        return [2..hours().ago().getUnixEpoch(), Date.today().getUnixEpoch()];
      }
    },
    filter: {
      filter: function(data, col) {
        var points, row, _i, _len;

        points = [];
        for (_i = 0, _len = data.length; _i < _len; _i++) {
          row = data[_i];
          points.push({
            x: row[4],
            y: row[col]
          });
        }
        return points;
      },
      sum: function(data) {
        return Charts.filter.filter(data, 3);
      },
      avg: function(data) {
        return Charts.filter.filter(data, 0);
      }
    },
    render: {
      spark: function(data, element) {
        return nv.addGraph({
          generate: function() {
            var chart;

            chart = nv.models.sparkline().width(100).height(50);
            d3.select(element).datum(data).call(chart);
            return chart;
          }
        });
      },
      line: function(data, element) {
        return nv.addGraph({
          generate: function() {
            var chart;

            chart = nv.models.lineChart().width(280).height(160).showLegend(false);
            chart.xAxis.ticks(8).tickFormat(function(ut) {
              return d3.time.format("%m-%d %H:%M")(new Date(ut * 1000));
            });
            chart.yAxis.ticks(4).tickFormat(d3.format('.0f'));
            d3.select(element).datum(data).transition().duration(500).call(chart);
            return chart;
          }
        });
      }
    }
  };

  InfoPod = (function() {
    function InfoPod(sensor) {
      this.sensor = sensor;
      this.chart = __bind(this.chart, this);
      this.sparkline = __bind(this.sparkline, this);
      this.update = __bind(this.update, this);
      this.jq = $('#' + this.sensor.short);
      this.interval = null;
      this.update();
      this.start();
    }

    InfoPod.prototype.display = function(value) {
      return this.jq.find('.value').html(value);
    };

    InfoPod.prototype.update = function() {
      var _this = this;

      return $.getJSON("/data/current/" + this.sensor.id, function(data) {
        if (data && data.value) {
          InfoPod.lastUpdated = data.unix_epoch;
          return _this.display(data.value);
        }
      });
    };

    InfoPod.prototype.stop = function() {
      return clearInterval(this.interval);
    };

    InfoPod.prototype.start = function() {
      return this.interval = setInterval(this.update, 30000);
    };

    InfoPod.prototype.sparkline = function() {
      var end, start, _ref,
        _this = this;

      _ref = Charts.dates.spark(), start = _ref[0], end = _ref[1];
      return $.getJSON("/data/recent/" + this.sensor.id + "/" + start + "/" + end, function(data) {
        var point, points, row, _i, _len, _ref1;

        points = [];
        _ref1 = data.data;
        for (_i = 0, _len = _ref1.length; _i < _len; _i++) {
          row = _ref1[_i];
          point = {
            y: row[1],
            x: new Date(row[0] * 1000)
          };
          points.push(point);
        }
        return Charts.render.spark(points, _this.jq.find('.sparkline').get(0));
      });
    };

    InfoPod.prototype.chart = function() {
      var end, start, _ref,
        _this = this;

      _ref = Charts.dates.week(), start = _ref[0], end = _ref[1];
      return $.getJSON("/data/hourly/" + this.sensor.id + "/" + start + "/" + end, function(data) {
        var results;

        results = [
          {
            values: Charts.filter.avg(data.data),
            key: _this.sensor.short,
            color: '#F1601D'
          }
        ];
        return Charts.render.line(results, _this.jq.find('.chart').get(0));
      });
    };

    InfoPod.lastUpdated = 0;

    InfoPod.create = function(sensor) {
      switch (sensor.short) {
        case "Pumping":
          return new PumpingInfoPod(sensor);
        case "Water":
          return new WaterInfoPod(sensor);
        case "Temperature":
        case "Humidity":
        case "Moisture":
          return new TrendingInfoPod(sensor);
        default:
          return new InfoPod(sensor);
      }
    };

    return InfoPod;

  })();

  PumpingInfoPod = (function(_super) {
    __extends(PumpingInfoPod, _super);

    function PumpingInfoPod() {
      this.chart = __bind(this.chart, this);      _ref = PumpingInfoPod.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    PumpingInfoPod.prototype.display = function(value) {
      if (value === 1) {
        this.jq.find('i').addClass('icon-play').find('span').html('Pump is running');
      } else {
        this.jq.find('i').addClass('icon-stop').find('span').html('Pump is stopped');
      }
      return this.chart();
    };

    PumpingInfoPod.prototype.chart = function() {
      var end, start, _ref1,
        _this = this;

      _ref1 = Charts.dates.week(), start = _ref1[0], end = _ref1[1];
      return $.getJSON("/data/daily/" + this.sensor.id + "/" + start + "/" + end, function(data) {
        var results;

        results = [
          {
            values: Charts.filter.sum(data.data),
            key: _this.sensor.short,
            color: '#17A768'
          }
        ];
        return Charts.render.line(results, _this.jq.parents('.info').find('.chart').get(0));
      });
    };

    return PumpingInfoPod;

  })(InfoPod);

  WaterInfoPod = (function(_super) {
    __extends(WaterInfoPod, _super);

    function WaterInfoPod() {
      _ref1 = WaterInfoPod.__super__.constructor.apply(this, arguments);
      return _ref1;
    }

    WaterInfoPod.prototype.display = function(value) {
      if (value === 1) {
        return this.jq.find('i').addClass('icon-warning-sign').find('span').html('Not enough water!');
      } else {
        return this.jq.find('i').addClass('icon-ok').find('span').html('Plenty of water');
      }
    };

    return WaterInfoPod;

  })(InfoPod);

  TrendingInfoPod = (function(_super) {
    __extends(TrendingInfoPod, _super);

    function TrendingInfoPod() {
      _ref2 = TrendingInfoPod.__super__.constructor.apply(this, arguments);
      return _ref2;
    }

    TrendingInfoPod.prototype.display = function(value) {
      TrendingInfoPod.__super__.display.call(this, value);
      this.sparkline();
      return this.chart();
    };

    return TrendingInfoPod;

  })(InfoPod);

  SmallInfoPod = (function(_super) {
    __extends(SmallInfoPod, _super);

    function SmallInfoPod() {
      _ref3 = SmallInfoPod.__super__.constructor.apply(this, arguments);
      return _ref3;
    }

    return SmallInfoPod;

  })(InfoPod);

  pods = [];

  $(function() {
    var sensor, _i, _len, _results;

    _results = [];
    for (_i = 0, _len = sensors.length; _i < _len; _i++) {
      sensor = sensors[_i];
      _results.push(pods[sensor.id] = InfoPod.create(sensor));
    }
    return _results;
  });

  sensors = [
    {
      id: 1,
      short: "PanelLight",
      description: "Panel Light Level"
    }, {
      id: 2,
      short: "BedLight",
      description: "Bed Light Level"
    }, {
      id: 3,
      short: "Humidity",
      description: "Humidity"
    }, {
      id: 4,
      short: "Temperature",
      description: "Temperature"
    }, {
      id: 5,
      short: "Moisture",
      description: "Soil Moisture"
    }, {
      id: 6,
      short: "Water",
      description: "Water Level"
    }, {
      id: 7,
      short: "Pumping",
      description: "Pump Running"
    }
  ];

}).call(this);
