import sublime, sublime_plugin
import re
from datetime import datetime


class ReorderParagraphsSelectBibFileCommand(sublime_plugin.WindowCommand):
    def done(self, filename):
        settings = sublime.load_settings(__name__ + '.sublime-settings')
        settings.set('bibFile', filename)
        sublime.save_settings(__name__ + '.sublime-settings')


    def run(self):
        self.window.show_input_panel(
            "file to open: ", './bib_file.bib', self.done, None, None)


class ReorderParagraphsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        settings = sublime.load_settings(__name__ + '.sublime-settings')
        bib_location = settings.get('bibFile', './bibfile.bib')
        print(bib_location)
        with open(bib_location, encoding="utf-8") as f:
            bib_file = f.read()

        bib_dict = {}
        for bibitem in bib_file.split('\n\n'):
            if bibitem.startswith('@article'):
                bibitem_format = ''.join(bibitem.splitlines())
                ym = re.search(r'year = \{([0-9]{4})\}', bibitem_format)
                cm = re.search(r'@article\{(.*),author', bibitem_format)

                #print bibitem

                if ym is None:
                    print("Cannot find date for {0}".format(bibitem))
                elif cm is None:
                    print("Cannot find author for {0}".format(bibitem))
                else:
                    bib_dict[cm.groups(1)[0]] = datetime(year=int(ym.groups(1)[0]), month=1, day=1)

        selections = self.view.sel()
        for selection in selections:
            paragraphs = self.view.substr(selection).split('\n\n')
            order = range(len(paragraphs))
            times = []
            indices = []

            for i, textitem in enumerate(paragraphs):
                if textitem.startswith('\citep{') or textitem.startswith('\n\citep{'):
                    m = re.search(r'\citep{(.*?)}', textitem)
                    if m is None:
                        print("Cannot find citation in text block: {:s}".format(textitem))
                    else:
                        try:
                            times.append(bib_dict[m.groups(1)[0]])
                            indices.append(i)
                        except KeyError:
                            print("Cannot find entry for citation {:s}".format(m.groups(1)[0]))
                            times.append(datetime(year=1, month=1, day=1))
                            indices.append(i)

            #argsort function
            st = (i for i, _ in sorted(enumerate(times), key=lambda a: a.__getitem__(1)))

            new_paragraphs = list(paragraphs)
            for i, idx in enumerate(st):
                new_paragraphs[indices[i]] = paragraphs[indices[idx]]

            self.view.replace(edit, self.view.line(selection), '\n\n'.join(new_paragraphs))

