var gulp = require('gulp');
var connect = require('gulp-connect');
// var livereload = require('gulp-livereload');
var sass = require('gulp-sass');
// var concatCss = require('gulp-concat-css');
// var sourcemaps = require('gulp-sourcemaps');


// var path = require('./path');

gulp.task('connect', function () {
	connect.server({
		root: 'web',
		livereload: true
	})
});

gulp.task('css', function () {
	gulp.src('./res/sass/style.scss')
		.pipe(sass())
		// .pipe(concatCss('style.css'))
		.pipe(gulp.dest('./res/css'))
		// .pipe(connect.reload())
});

// gulp.task('js', () => {
// 	gulp.src(path.src.js)
// 		.pipe(sourcemaps.init())
// 		.pipe(babel({
//             presets: ["es2015"],
//             plugins: ["transform-object-rest-spread"]
//         }))
// 		.pipe(sourcemaps.write())
// 		.pipe(gulp.dest(path.web.js))
// 		.pipe(connect.reload())
// });

gulp.task('watch', function () {
	gulp.watch('./res/sass/**/*.scss', ['css']);
});

gulp.task('default', [ 'css', 'watch']);