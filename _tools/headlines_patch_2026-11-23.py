"""2026-11-23 (Jenn): shorter page headlines (Hero Callout: under 40 characters), no em dashes.
Changes only the headline column of data.txt; nav labels and breadcrumbs keep the real names.
Run: python3 headlines_patch.py <prototype-hub>"""
import sys, pathlib
NEW = {
 "Discoveries that change lives—in Indiana and beyond": "Discoveries that change lives",
 "Own your Hoosier journey—with the strength of IU behind you": "Own your Hoosier journey",
 "Stay connected to a network 806,000+ strong": "Stay connected to 806,000+ Hoosiers",
 "Your degree. Your career. Your next step starts here.": "Your degree. Your career. Your future.",
 "Turn your passions into a purpose-driven degree": "Turn your passions into a degree",
 "The science of today and the tools for tomorrow": "Today’s science, tomorrow’s tools",
 "Challenge yourself with an honors education at IU Bloomington": "Challenge yourself with honors",
 "Explore your options and still graduate in four years": "Explore and still graduate in four years",
 "Fast-track your future with an accelerated master’s degree": "Earn your master’s degree faster",
 "Learn and live in the best environment for you": "Live and learn where you thrive",
 "Everything you need to register for classes": "Register for classes",
 "Manage your academic records and student status": "Manage your academic records",
 "Atlas for International Students and Scholars": "Atlas for international students",
 "About the use of test scores in admissions": "How we use test scores",
 "Application process for transfer students": "Apply as a transfer student",
 "Key transfer student application deadlines": "Transfer application deadlines",
 "Application process for intercampus transfer students": "Apply as an intercampus transfer",
 "Application process for future graduate students": "Apply as a graduate student",
 "Get a fee waiver or reduced fee when you apply": "Lower or waive your application fee",
 "Application process for military & veteran applicants": "Apply as a military or veteran student",
 "Frequently asked questions about applying": "Questions about applying",
 "A guaranteed path for Indiana residents earning the Indiana Diploma with the Enrollment Honors Plus Seal": "A guaranteed path for Indiana residents",
 "Educational opportunities your child can feel good about": "Opportunities you can feel good about",
 "Prepare for your future at IU Bloomington": "Prepare for your future at IU",
 "Increasing opportunity for Indiana students": "More opportunity for Indiana students",
 "Attend your Foundations of Orientation program": "Attend your orientation program",
 "Work with the Office of Orientation & Enrollment Programs": "Work with the orientation team",
 "Your guide to graduate student orientation": "Graduate student orientation",
 "Enrollment process for transfer students and spring freshmen": "Enroll as a transfer or spring freshman",
 "Enrollment steps for international students": "Enrollment for international students",
 "Enrollment process for international freshman students": "Enroll as an international freshman",
 "Enrollment process for international transfer students": "Enroll as an international transfer",
 "Enrollment process for international graduate students": "Enroll as an international grad student",
 "Enrollment process for intercampus transfer students": "Enroll as an intercampus transfer",
 "See how much it costs to attend IU Bloomington": "See what IU Bloomington costs",
 "See the full value of an IU graduate degree": "The value of an IU graduate degree",
 "Irving and Lena Lo (ILLO) Scholarship Fund": "The ILLO Scholarship Fund",
 "Explore what’s happening at IU Bloomington": "See what’s happening on campus",
 "Celebrating 250 years of the American story": "250 years of the American story",
 "Revolution and Reflection self-guided tour": "Revolution and Reflection tour",
 "Find building abbreviations for IU Bloomington": "Campus building abbreviations",
 "Continuing a legacy of innovative solutions": "A legacy of innovative solutions",
 "Keeping current with research at IU Bloomington": "The latest IU Bloomington research",
 "IU Bloomington is full of people who will help you succeed": "People here want you to succeed",
 "Get a head start on your career with work experience": "Get a head start on your career",
 "Support for your financial and everyday needs": "Help with money and everyday needs",
 "Guiding Indiana University’s flagship campus": "Leading IU’s flagship campus",
 "Celebrating the people who move IU forward": "The people who move IU forward",
 "Congratulations Christoph Irmscher and David Polly": "Congratulations, Irmscher and Polly",
 "Congratulations Brea Perry, Bernice Pescosolido, and Kosali Simon": "Congratulations to three IU faculty",
 "Congratulations to the Indiana Daily Student and Arbutus": "Congratulations, IDS and Arbutus",
 "Congratulations to Indiana University Football": "Congratulations, IU Football",
 "Congratulations Paige Andersson and Rachael Jones McAfee": "Congratulations, Andersson and McAfee",
 "Congratulations to the Jacobs School of Music": "Congratulations, Jacobs School of Music",
}
assert all(len(v) <= 40 and '—' not in v and '–' not in v for v in NEW.values())
p = pathlib.Path(sys.argv[1])/'_tools'/'bloomington'/'data.txt'
out, used, left = [], set(), []
for line in p.read_text().splitlines():
    f = line.split('|')
    if len(f) >= 5:
        h = f[2] if f[3] == '=' else f[3]
        if h in NEW: f[3] = NEW[h]; used.add(h); h = f[3]
        if len(h) > 40 or '—' in h or '–' in h: left.append(h)
    out.append('|'.join(f))
p.write_text('\n'.join(out) + '\n')
print('changed', len(used), 'of', len(NEW), '| still long or dashed:', left)
