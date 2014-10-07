%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  IEEE.bst  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Bibliography Syle file for articles according to IEEE instructions
% balemi@aut.ee.ethz.ch     <22-JUN-93>
% modified from unsrt.bib. Contributions by Richard H. Roy

ENTRY
  { address
    author
    booktitle
    chapter
    edition
    editor
    howpublished
    institution
    journal
    key
    month
    note
    number
    organization
    pages
    publisher
    school
    series
    title
    type
    volume
    year
  }
  {}
  { label }

READ

STRINGS { longest.label }

INTEGERS { number.label longest.label.width }

FUNCTION {initialize.longest.label}
{ "" 'longest.label :=
  #1 'number.label :=
  #0 'longest.label.width :=
}

FUNCTION {longest.label.pass}
{ number.label int.to.str$ 'label :=
  number.label #1 + 'number.label :=
  label width$ longest.label.width >
    { label 'longest.label :=
      label width$ 'longest.label.width :=
    }
    'skip$
  if$
}

FUNCTION {format.article.crossref}
{ key empty$
    { 
      journal empty$
        { "need key or journal for " cite$ * " to crossref " * crossref * warning$ "" }
        { "In {\em " journal * "\/}" * }
      if$
    }
    { "In " key * }
    if$
    " \cite{" * crossref * "}" *
}

ITERATE {format.article.crossref}