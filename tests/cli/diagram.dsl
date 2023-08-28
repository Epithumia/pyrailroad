Stack:
    Choice: 1
        Terminal: foo
        NonTerminal raw: bar
        ZeroOrMore:
            Terminal: z1
            Terminal: z2
        OneOrMore:
            Terminal: baz
            Comment: and again...
        Sequence:
            Terminal: s1
            Terminal: s2
            Optional:
                Sequence:
                    Terminal: o1
                    Terminal: o2
                    Terminal: o3
            Choice: 1
                Terminal raw: c1
                Terminal html: c2
                Terminal: c3
        MultipleChoice: 0 any
            Terminal: mc1
    Terminal: ter1
    Terminal: ter2
    HorizontalChoice:
        Choice: 0
            Terminal: hc1
            Terminal: hc2
        Choice: 0
            Terminal: hc3
            Terminal: hc4
    Group:
        Sequence:
            Terminal: g1
            Terminal: g2
    Group: group label
        Terminal: gl
    OptionalSequence:
        Terminal: opt1
        Terminal: opt2
        Terminal: opt3
    AlternatingSequence:
        Terminal: alt1
        Terminal: alt2