(defun gps-line ()
  "Print the current buffer line number and narrowed line number of point."
  (interactive)
  (let (
	(start (point-min))
	(n (line-number-at-pos))
	(num_lines (count-matches "\n" 0))
	)
    (if (= start 1)
	(message "Line %d/%d" n num_lines)
      (save-excursion
	(save-restriction
	  (widen)
	  (message "line %d (narrowed line %d)"
		   (+ n (line-number-at-pos start) -1) n))))))
