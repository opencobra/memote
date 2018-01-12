var gulp = require('gulp');
var inline = require('gulp-inline');
var minify = require('gulp-minify');
  // , uglify = require('gulp-uglify')
  // , minifyCss = require('gulp-minify-css')
  // , autoprefixer = require('gulp-autoprefixer');

function inlining() {
  return gulp.src('dist/index.html')
    .pipe(inline({
      base: 'dist/',
      js: minify
      // css: [minifyCss, autoprefixer({ browsers:['last 2 versions'] })],
      // disabledTypes: ['svg', 'img', 'js'], // Only inline css files
      // ignore: ['./css/do-not-inline-me.css']
    }))
    .pipe(gulp.dest('build/'));
}

gulp.task('inline', inlining);
