SRCS = $(shell find dataset-txt -name '*.in')
TARGETS = $(SRCS:dataset-txt/%.in=dataset-txt/%.out)
TF_TARGETS = $(SRCS:dataset-txt/%.in=dataset-txt/%.thefuck)
.DEFAULT_GOAL = gen

.PHONY : gen gen-thefuck clean

dataset-txt/%.out : dataset-txt/%.in shellfix.py
	@echo '(' `find dataset-txt -name '*.out' | wc -l` of `ls dataset-txt/*.in | wc -l` ')'
	@echo + [GEN]\\t$@
	@head -1 $< | timeout 600s time ./shellfix.py > $@ 2>&1

dataset-txt/%.thefuck : dataset-txt/%.in 
	@echo '(' `find dataset-txt -name '*.thefuck' | wc -l` of `ls dataset-txt/*.in | wc -l` ')'
	@echo + [GEN]\\t$@
	@time thefuck -y `head -1 $<` 2> /dev/null > $@ || true 

gen : $(TARGETS)

gen-thefuck : $(TF_TARGETS)

clean :
	rm -f dataset-txt/*.out
