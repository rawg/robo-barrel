
exec = require('child_process').exec
pkg = require './package.json'
config = require './config.json'

growl = (title, message) ->
    exec "growlnotify -m '#{message}' --image .grunt/grunt-logo.jpeg -n 'Grunt' '#{title}'"

db =
    schema: () ->
        exec "sqlite3 #{config.db} < db/schemasql", (error, stdout, stderr) ->
            if error is not null
                console.log stderr
                growl error, stderr

    data: () ->
        exec "sqlite3 #{config.db} < db/insert.sql"

module.exports = (grunt) ->
    grunt.task.loadNpmTasks 'grunt-contrib-watch'
    grunt.task.loadNpmTasks 'grunt-contrib-coffee'
    grunt.task.loadNpmTasks 'grunt-contrib-stylus'
    grunt.task.loadNpmTasks 'grunt-contrib-jade'
    
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
    grunt.registerTask 'db', () ->
        db.schema()
        db.data()
