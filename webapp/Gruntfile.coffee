
exec = require('child_process').exec
pkg = require './package.json'
config = require './config.json'
path = require 'path'
fs = require 'fs'

module.exports = (grunt) ->
    grunt.task.loadNpmTasks 'grunt-contrib-watch'
    grunt.task.loadNpmTasks 'grunt-contrib-coffee'
    grunt.task.loadNpmTasks 'grunt-contrib-stylus'
    grunt.task.loadNpmTasks 'grunt-contrib-jade'
    
    # Send a message to Growl
    growl = (title, message) ->
        exec "growlnotify -m '#{message}' --image .grunt/grunt-logo.jpeg -n 'Grunt' '#{title}'"
    
    # Run a command and, optionally, execute a call back
    # (like grunt-shell but that's not working consistently)
    run = (command, callback) ->
        proc = exec command
        
        stdout = ''
        stderr = ''
        proc.stdout.on 'data', (data) -> stdout += data
        proc.stderr.on 'data', (data) -> stderr += data

        proc.on 'exit', (status, signal) ->
            callback status, stdout, stderr


    # Database creation and initialization operations
    database =
        schema: ->
            done = this.async()
            run "sqlite3 #{config.db} < db/schema.sql", (status, stdout, stderr) -> done not status > 0
    
        testdata: ->
            done = this.async()
            run "python service/create_test_data.py", (status, stdout, stderr) -> done not status > 0

    arduino = 
        defines: ->
            done = this.async()
            
            defines = "\n"

            for sensor in config.sensors
                defines += "#define SENSOR_#{sensor[2]} #{sensor[0]}\n"

            defines += "\n"

            fs.writeFile path.join(path.dirname(__dirname), '/rainduino/sensors.h'), defines, (err, data) ->
                if err
                    done false
                else
                    done true
    
    # Growl errors and warnings
    ["warn", "fatal"].forEach (level) ->
        grunt.util.hooker.hook grunt.fail, level, (opt) ->
            growl "#{pkg.name}: #{opt.name}", opt.message

    grunt.initConfig
        coffee:
            compile:
                files:
                    'ui/static/js/app.js': 'ui/src/coffee/**/*.coffee'

        stylus:
            compile:
                files:
                    'ui/static/css/styles.css': 'ui/src/stylus/**/*.styl'

        jade:
            compile:
                expand: true
                flatten: false
                cwd: 'ui/src/jade'
                src: ['**/*.jade']
                dest: 'ui/static/'
                ext: '.html'

        watch:
            files: ['ui/src/coffee/**/*.coffee', 'ui/src/stylus/**/*.styl', 'ui/src/jade/**/*.jade']
            tasks: ['coffee:compile', 'stylus:compile', 'jade:compile']

    grunt.registerTask 'default', ['coffee', 'stylus', 'jade']
    grunt.registerTask 'schema', 'Initialize database schema', database.schema
    grunt.registerTask 'testdata', 'Generate test data', database.testdata
    grunt.registerTask 'defines', 'Generate defines for sensor IDs', arduino.defines
