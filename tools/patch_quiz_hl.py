# -*- coding: utf-8 -*-
"""Patch make_quiz.py so a preselected bank item is highlighted."""

p = r"E:\CST\408\tools\make_quiz.py"
c = open(p, encoding="utf-8").read()

REPS = [
    ('''<button data-v="${t.id}">${esc(t.name)}''',
     '''<button data-v="${t.id}" class="${st.topic===t.id?'on':''}">${esc(t.name)}'''),
    ('''<button data-v="${k}" style="--ac:${ACC[k]}">${SUBJ[k]}''',
     '''<button data-v="${k}" class="${st.subj===k?'on':''}" style="--ac:${ACC[k]}">${SUBJ[k]}'''),
    ('''<button data-v="${esc(ck)}" style="--ac:${ACC[s]}">${esc(c)}''',
     '''<button data-v="${esc(ck)}" class="${st.chap===ck?'on':''}" style="--ac:${ACC[s]}">${esc(c)}'''),
    ('''<button data-v="${k}" style="--ac:${ACC[v.s]}">${hot}${esc(v.name)}''',
     '''<button data-v="${k}" class="${st.kp===k?'on':''}" style="--ac:${ACC[v.s]}">${hot}${esc(v.name)}'''),
    ('''<button data-v="${y}">${y} 年''',
     '''<button data-v="${y}" class="${st.year==y?'on':''}">${y} 年'''),
    ('''<button data-v="must">必考级''',
     '''<button data-v="must" class="${st.freq==='must'?'on':''}">必考级'''),
    ('''<button data-v="high">高频''',
     '''<button data-v="high" class="${st.freq==='high'?'on':''}">高频'''),
    ('''<button data-v="common">常考''',
     '''<button data-v="common" class="${st.freq==='common'?'on':''}">常考'''),
    ('''<button data-v="rare">低频''',
     '''<button data-v="rare" class="${st.freq==='rare'?'on':''}">低频'''),
]

n = 0
for a, b in REPS:
    if a in c and b not in c:
        c = c.replace(a, b)
        n += 1
open(p, "w", encoding="utf-8").write(c)
print(f"patched {n}/{len(REPS)}")
