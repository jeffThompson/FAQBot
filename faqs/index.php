<html>
<head>
	<title>FAQ Generator</title>
	<link href='https://fonts.googleapis.com/css?family=Crimson+Text:400,700' rel='stylesheet' type='text/css'>
	<link href="include/stylesheet.css" rel="stylesheet" type="text/css">
</head>

<body>
	<div id="wrapper">
		<h1>FAQ Generator</h1>
		<hr />
		
		<p>Available FAQs:</p>
		<ul id="tableOfContents">
		<?php
			$files = glob('*.html');
			natcasesort($files);
			foreach ($files as $file) {
				$item = basename($file, '.html');
				$item = str_replace('_', ' ', $item);
				if ($item == 'index') {
					continue;
				}
				echo '<li><a href="' . $item . '.html">' . $item . '</a></li>' . PHP_EOL;
			}
		?>
		</ul>

		<hr />
		<footer>
			<ul>
				<li>More FAQs <a href="https://twitter.com/faqgenerator">@faqgenerator</a></li>
				<li>A project by <a href="http://www.jeffreythompson.org">Jeff Thompson</a></li>
			</ul>
		</footer>
	</div> <!-- end wrapper -->

	<!-- nice smart quotes, via: http://smartquotesjs.com -->
	<script src="include/smartquotes.min.js"></script>
</body>
</html>