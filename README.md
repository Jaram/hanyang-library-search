# hanyang-library-search

## Requirements

- lxml
- requests


## Examples

### searching books about 'programming'

	import library.books

	books_on_page_1 = library.books.search('keyword', 'programming', 1)
	books_on_page_2 = library.books.search('keyword', 'programming', 2)

### fetching an information of the book

	import library.book

	identifier = '000001231912'
	head_first_programming = library.book.serach(identifier)