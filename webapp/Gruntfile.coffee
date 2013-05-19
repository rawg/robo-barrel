
exec = require('child_process').exec
pkg = require './package.json'
config = require './config.json'

module.exports = (grunt) ->
    grunt.task.loadNpmTasks 'grunt-contrib-watch'
    grunt.task.loadNpmTasks 'grunt-contrib-coffee'
    grunt.task.loadNpmTasks 'grunt-contrib-stylus'
    grunt.task.loadNpmTasks 'grunt-contrib-jade'
    grunt.task.loadNpmTasks 'grunt-shell'
    
    # Send a message to Growl
    growl = (title, message) ->
        exec "growlnotify -m '#{message}' --image .grunt/grunt-logo.jpeg -n 'Grunt' '#{title}'"

    # Process results from grunt-shell
    handleShellOutput = (err, stdout, stderr, cb) ->
        console.log err, stdout, stderr
        if err > 0
            grunt.fail.warn(stderr if stderr.length else stdout)
        cb()

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

        shell:
            schema:
                command: "sqlite3 #{config.db} < db/schemasql"
                stdout: true
                stderr: true
                #callback: handleShellOutput

            testData:
                command: "python create_test_data.py"
                stdout: true
                stderr: true
                callback: handleShellOutput
                execOptions:
                    cwd: "./service"
        
        watch:
            files: ['ui/src/coffee/**/*.coffee', 'ui/src/stylus/**/*.styl', 'ui/src/jade/**/*.jade']
            tasks: ['coffee:compile', 'stylus:compile', 'jade:compile']

    grunt.registerTask 'default', ['coffee', 'stylus', 'jade']

