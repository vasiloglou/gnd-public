import sys,pytest,gnd
class Gate:
 def __init__(self): self.skips=[];self.passed=0
 def pytest_collectreport(self,report):
  if report.skipped:self.skips.append(report.nodeid)
 def pytest_runtest_logreport(self,report):
  if report.skipped:self.skips.append(report.nodeid)
  if report.when=='call' and report.passed:self.passed+=1
p=Gate()
code=pytest.main(['-q','--tb=line','-p','no:cacheprovider',*sys.argv[1:]],plugins=[p])
print('code',code,'passed',p.passed,'skips',p.skips[:5])
