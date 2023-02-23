'''

FIXME:	Skript pocita prechod pracovneho dna polnocou.

DAT Input:

	0	1					2	3	4	5
	+---+-------------------+---+---+---+
    1	2019-03-11 07:29:57	1	0	1	0
    1	2019-03-11 07:34:48	1	1	1	0
    2	2019-03-12 07:39:57	1	0	1	0
    2	2019-03-12 07:40:27	1	3	1	0
    1	2019-03-13 08:08:23	1	0	1	0


CSV Output:

	User;Date;WorkBegin;WorkEnd;BreakBegin;BreakEnd;OvertimeBegin;OvertimeEnd;

'''
from datetime import datetime
import sys


class AttendanceLogConverter:

	ACTION_ARRIVAL = 0
	ACTION_DEPARTURE = 1
	ACTION_BREAK_ARRIVAL = 3
	ACTION_BREAK_DEPARTURE = 2
	ACTION_OVERTIME_ARRIVAL = 4
	ACTION_OVERTIME_DEPARTURE = 5

	INDEX_USER = 0
	INDEX_TIMESTAMP = 1
	INDEX_ACTION = 3

	csv_struct = ['User', 'Date', 'WorkBegin', 'WorkEnd', 'BreakBegin', 'BreakEnd', 'OvertimeBegin', 'OvertimeEnd']

	def __init__(self, filename):
		self.out_filename = filename.replace('.dat', '.csv')
		self.data = []
		self.objects = {}
		fin = open(filename, 'r')
		lines = fin.readlines()
		for line in lines:
			self.data.append(tuple(line.strip().split('\t')))
		fin.close()

	def convert(self):
		line_nr = 1
		for l in self.data:
			assert len(l) == 6, \
				'Elements not match: %s line: %s' % (len(l), line_nr)
			who = '#%s' % l[self.INDEX_USER]
			ts = datetime.strptime(l[self.INDEX_TIMESTAMP], '%Y-%m-%d %H:%M:%S')
			action = int(l[self.INDEX_ACTION])
			self._add(who, action, ts)
			line_nr += 1
		done = self._opt_dates(self._opt_actions())
		self._export_csv(done)
		return (0, line_nr, len(done))

	def _add(self, who, action, timestamp):
		if who in self.objects.keys():
			self.objects[who].append((action, timestamp))
		else:
			self.objects[who] = [(action, timestamp)]

	def _export_csv(self, objects):
		header = ';'.join(self.csv_struct) + ';\n'
		lines = []
		for o in objects:
			who, dates = o
			for d in dates:
				lines.append((who, d[0], d[1], d[2], d[3], d[4], d[5], d[6]))
		lines_fmt = []
		for l in lines:
			s = ''
			for _ in l:
				s += "%s;" % _
			lines_fmt.append(s)
		body = '\n'.join(lines_fmt)
		f_out = open(self.out_filename, 'w')
		f_out.write(header + body)
		f_out.close()

	def _opt_actions(self):
		done = []
		for u in self.objects.keys():
			works_b, works_e = [], []
			break_b, break_e = [], []
			overtime_b, overtime_e = [], []
			for o in self.objects[u]:
				a, t = o
				if a == self.ACTION_ARRIVAL:
					works_b.append(t)
				if a == self.ACTION_DEPARTURE:
					works_e.append(t)
				if a == self.ACTION_BREAK_ARRIVAL:
					break_b.append(t)
				if a == self.ACTION_BREAK_DEPARTURE:
					break_e.append(t)
				if a == self.ACTION_OVERTIME_ARRIVAL:
					overtime_b.append(t)
				if a == self.ACTION_OVERTIME_DEPARTURE:
					overtime_e.append(t)
			done.append((u, works_b, works_e, break_b,
						break_e, overtime_b, overtime_e))
		return done

	def _opt_dates(self, objects):
		done = []
		for o in objects:
			u = o[0]
			t = []
			for _ in o[1]:
				t.append(_.date())
			t = list(set(t))
			w = []
			for d in t:
				_w_ari = self._pom_min(d, o[1])
				_w_dep = self._pom_max(d, o[2])
				_b_ari = self._pom_min(d, o[3])
				_b_dep = self._pom_max(d, o[4])
				_o_ari = self._pom_min(d, o[5])
				_o_dep = self._pom_max(d, o[6])
				w.append((d, _w_ari, _w_dep, _b_ari, _b_dep, _o_ari, _o_dep))
			done.append((u, w))
		return done

	def _pom_min(self, date, objects):
		none = datetime(date.year, date.month, date.day, 0, 0, 0)
		m = []
		for o in objects:
			if o.date() == date:
				m.append(o)
		if len(m):
			return min(m)
		return none

	def _pom_max(self, date, objects):
		none = datetime(date.year, date.month, date.day, 0, 0, 0)
		m = []
		for o in objects:
			if o.date() == date:
				m.append(o)
		if len(m):
			return max(m)
		return none


if __name__ == '__main__':
	if len(sys.argv) == 2:
		converter = AttendanceLogConverter(sys.argv[1])
		rc, total_items, total_objects = converter.convert()
		if rc == 0:
			print('Done. Converted %s log items to %s objects.' % \
			(total_items, total_objects))
		sys.exit(rc)
	print('Usage: %s <att-log.dat>' % sys.argv[0])
