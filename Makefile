SRCS = $(shell find dataset-txt -name '*.in')
TARGETS = $(SRCS:dataset-txt/%.in=dataset-txt/%.out)
.DEFAULT_GOAL = gen

.PHONY : gen clean

dataset-txt/%.out : dataset-txt/%.in shellfix.py
	@echo '(' `find dataset-txt -name '*.out' | wc -l` of `ls dataset-txt/*.in | wc -l` ')'
	@echo + [GEN]\\t$@
	@head -1 $< | timeout 600s time ./shellfix.py > $@ 2>&1

gen : $(TARGETS)

clean :
	rm -f dataset-txt/*.out