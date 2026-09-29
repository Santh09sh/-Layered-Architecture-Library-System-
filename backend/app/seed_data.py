"""
Seed Data
Populates the database with realistic sample data for demonstration.
Run: python -m app.seed_data
"""

from datetime import datetime, timedelta
import random
from app.database import SessionLocal, init_db
from app.business.auth_service import AuthService
from app.domain.entities.user import User
from app.domain.entities.book import Book
from app.domain.entities.author import Author
from app.domain.entities.publisher import Publisher
from app.domain.entities.category import Category
from app.domain.entities.book_copy import BookCopy
from app.domain.entities.borrow_record import BorrowRecord
from app.domain.entities.review import Review
from app.domain.entities.notification import Notification
from app.domain.enums import (
    UserRole, UserStatus, BookCopyStatus, BookCondition,
    BorrowStatus, NotificationType,
)


def seed():
    print("🌱 Initializing database...")
    init_db()

    db = SessionLocal()
    auth = AuthService(db)

    # Check if data already exists
    if db.query(User).count() > 0:
        print("⚠️  Database already has data. Skipping seed.")
        db.close()
        return

    print("👤 Creating users...")

    # --- Admin & Librarian ---
    admin = User(
        name="Admin User", email="admin@library.edu",
        password_hash=auth.hash_password("admin123"),
        role=UserRole.ADMIN, status=UserStatus.ACTIVE,
    )
    librarian1 = User(
        name="Sarah Johnson", email="sarah@library.edu",
        password_hash=auth.hash_password("librarian123"),
        role=UserRole.LIBRARIAN, phone="+1-555-0101", status=UserStatus.ACTIVE,
    )
    librarian2 = User(
        name="Michael Chen", email="michael@library.edu",
        password_hash=auth.hash_password("librarian123"),
        role=UserRole.LIBRARIAN, phone="+1-555-0102", status=UserStatus.ACTIVE,
    )

    db.add_all([admin, librarian1, librarian2])
    db.flush()

    # --- Students ---
    students_data = [
        ("Vishnu Reddy", "vishnu@university.edu", "STU001"),
        ("Aisha Patel", "aisha@university.edu", "STU002"),
        ("James Wilson", "james@university.edu", "STU003"),
        ("Maria Garcia", "maria@university.edu", "STU004"),
        ("David Kim", "david@university.edu", "STU005"),
        ("Emma Thompson", "emma@university.edu", "STU006"),
        ("Raj Mehta", "raj@university.edu", "STU007"),
        ("Sophie Anderson", "sophie@university.edu", "STU008"),
        ("Alex Rivera", "alex@university.edu", "STU009"),
        ("Fatima Al-Hassan", "fatima@university.edu", "STU010"),
        ("Lucas Brown", "lucas@university.edu", "STU011"),
        ("Priya Sharma", "priya@university.edu", "STU012"),
        ("Oliver Davis", "oliver@university.edu", "STU013"),
        ("Yuki Tanaka", "yuki@university.edu", "STU014"),
        ("Isabella Martinez", "isabella@university.edu", "STU015"),
        ("Hassan Ali", "hassan@university.edu", "STU016"),
        ("Chloe Walker", "chloe@university.edu", "STU017"),
        ("Daniel Lee", "daniel@university.edu", "STU018"),
        ("Grace O'Brien", "grace@university.edu", "STU019"),
        ("Mohammed Rahman", "mohammed@university.edu", "STU020"),
    ]

    students = []
    for name, email, sid in students_data:
        student = User(
            name=name, email=email,
            password_hash=auth.hash_password("student123"),
            role=UserRole.STUDENT, student_id=sid, status=UserStatus.ACTIVE,
        )
        students.append(student)

    db.add_all(students)
    db.flush()

    print("📂 Creating categories...")

    categories_data = [
        ("Software Engineering", "Books about software development, design patterns, and best practices"),
        ("Artificial Intelligence", "Machine learning, deep learning, and AI fundamentals"),
        ("Data Science", "Data analysis, statistics, and visualization"),
        ("Computer Networks", "Networking, protocols, and distributed systems"),
        ("Operating Systems", "OS concepts, kernel design, and system programming"),
        ("Database Systems", "Relational databases, NoSQL, and data management"),
        ("Cybersecurity", "Information security, cryptography, and ethical hacking"),
        ("Web Development", "Frontend, backend, and full-stack web technologies"),
        ("Mathematics", "Calculus, linear algebra, and discrete mathematics"),
        ("Algorithms", "Algorithm design, complexity analysis, and data structures"),
    ]

    categories = []
    for name, desc in categories_data:
        cat = Category(name=name, description=desc)
        categories.append(cat)

    db.add_all(categories)
    db.flush()

    print("🏢 Creating publishers...")

    publishers_data = [
        ("O'Reilly Media", "https://www.oreilly.com", "Sebastopol, CA"),
        ("Pearson Education", "https://www.pearson.com", "London, UK"),
        ("Addison-Wesley", "https://www.informit.com", "Boston, MA"),
        ("MIT Press", "https://mitpress.mit.edu", "Cambridge, MA"),
        ("Springer", "https://www.springer.com", "Berlin, Germany"),
        ("McGraw-Hill", "https://www.mheducation.com", "New York, NY"),
        ("Manning Publications", "https://www.manning.com", "Shelter Island, NY"),
        ("Packt Publishing", "https://www.packtpub.com", "Birmingham, UK"),
        ("Cambridge University Press", "https://www.cambridge.org", "Cambridge, UK"),
        ("Wiley", "https://www.wiley.com", "Hoboken, NJ"),
    ]

    publishers = []
    for name, website, address in publishers_data:
        pub = Publisher(name=name, website=website, address=address)
        publishers.append(pub)

    db.add_all(publishers)
    db.flush()

    print("✍️  Creating authors...")

    authors_data = [
        ("Robert C. Martin", "Software engineer, author of Clean Code", "American"),
        ("Martin Fowler", "Software developer specializing in OOD and refactoring", "British"),
        ("Andrew Ng", "AI pioneer, co-founder of Coursera", "British-American"),
        ("Stuart Russell", "Computer science professor at UC Berkeley", "British"),
        ("Peter Norvig", "Director of Research at Google", "American"),
        ("Thomas H. Cormen", "Professor of computer science at Dartmouth", "American"),
        ("Donald Knuth", "The father of algorithm analysis", "American"),
        ("Andrew S. Tanenbaum", "Professor of computer science at VU Amsterdam", "American"),
        ("Erich Gamma", "Software engineer, co-author of Design Patterns", "Swiss"),
        ("Joshua Bloch", "Software engineer, author of Effective Java", "American"),
        ("Aurélien Géron", "Machine learning consultant and author", "French"),
        ("Wes McKinney", "Creator of pandas, data science advocate", "American"),
        ("Brian Kernighan", "Computer scientist, co-author of The C Programming Language", "Canadian"),
        ("Eric Evans", "Creator of Domain-Driven Design", "American"),
        ("Hadley Wickham", "Chief Scientist at RStudio", "New Zealander"),
    ]

    authors = []
    for name, bio, nationality in authors_data:
        author = Author(name=name, biography=bio, nationality=nationality)
        authors.append(author)

    db.add_all(authors)
    db.flush()

    print("📚 Creating books...")

    books_data = [
        # (isbn, title, description, year, pages, publisher_idx, category_idx, author_idxs, rating)
        ("978-0132350884", "Clean Code", "A handbook of agile software craftsmanship. Even bad code can function, but if it isn't clean, it can bring a development organization to its knees.", 2008, 464, 2, 0, [0], 4.7),
        ("978-0201633610", "Design Patterns", "Elements of reusable object-oriented software. Gang of Four classic.", 1994, 416, 2, 0, [8], 4.5),
        ("978-0134757599", "Refactoring", "Improving the design of existing code. The definitive guide to refactoring.", 2018, 448, 2, 0, [1], 4.6),
        ("978-0596007126", "Head First Design Patterns", "A brain-friendly guide to design patterns using Java examples.", 2004, 694, 0, 0, [8], 4.4),
        ("978-0321125217", "Domain-Driven Design", "Tackling complexity in the heart of software.", 2003, 560, 2, 0, [13], 4.3),
        ("978-0262039246", "Deep Learning", "An introduction to a broad range of topics in deep learning.", 2016, 800, 3, 1, [2], 4.5),
        ("978-1492032649", "Hands-On Machine Learning", "Concepts, tools, and techniques to build intelligent systems.", 2019, 856, 0, 1, [10], 4.8),
        ("978-0262046824", "Artificial Intelligence: A Modern Approach", "The most popular textbook on AI used in universities worldwide.", 2020, 1136, 4, 1, [3, 4], 4.6),
        ("978-0262033848", "Introduction to Algorithms", "The comprehensive textbook on algorithms known as CLRS.", 2009, 1312, 3, 9, [5], 4.4),
        ("978-0201896831", "The Art of Computer Programming", "Knuth's magnum opus on fundamental algorithms.", 1997, 672, 2, 9, [6], 4.7),
        ("978-0132126953", "Modern Operating Systems", "Comprehensive guide to operating system design and implementation.", 2014, 1136, 1, 4, [7], 4.3),
        ("978-0133591620", "Computer Networks", "Top-down approach to computer networking.", 2014, 960, 1, 3, [7], 4.2),
        ("978-1491957660", "Python for Data Analysis", "Data wrangling with pandas, NumPy, and IPython.", 2017, 544, 0, 2, [11], 4.4),
        ("978-0131103627", "The C Programming Language", "The classic K&R C reference.", 1988, 272, 1, 0, [12], 4.6),
        ("978-0134685991", "Effective Java", "Best practices for the Java platform.", 2018, 416, 2, 0, [9], 4.7),
        ("978-1491950357", "JavaScript: The Good Parts", "Uncovering the good parts of JavaScript.", 2008, 176, 0, 7, [12], 4.2),
        ("978-0321127426", "Patterns of Enterprise Application Architecture", "Enterprise software patterns and practices.", 2002, 560, 2, 0, [1], 4.4),
        ("978-1098125974", "Designing Data-Intensive Applications", "The big ideas behind reliable, scalable, and maintainable systems.", 2017, 616, 0, 5, [1], 4.8),
        ("978-0596517748", "The Pragmatic Programmer", "Your journey to mastery in software development.", 2019, 352, 2, 0, [0], 4.6),
        ("978-1491950296", "Learning Python", "Powerful object-oriented programming with Python.", 2013, 1648, 0, 0, [12], 4.3),
    ]

    books = []
    for isbn, title, desc, year, pages, pub_idx, cat_idx, author_idxs, rating in books_data:
        book = Book(
            isbn=isbn, title=title, description=desc,
            publication_year=year, pages=pages,
            publisher_id=publishers[pub_idx].id,
            category_id=categories[cat_idx].id,
            average_rating=rating, total_ratings=random.randint(10, 200),
            cover_image=f"https://covers.openlibrary.org/b/isbn/{isbn.replace('-', '')}-L.jpg",
        )
        for aidx in author_idxs:
            book.authors.append(authors[aidx])
        books.append(book)

    db.add_all(books)
    db.flush()

    print("📋 Creating book copies...")

    copies = []
    locations = ["Shelf A1", "Shelf A2", "Shelf B1", "Shelf B2", "Shelf C1",
                 "Shelf C2", "Shelf D1", "Shelf D2", "Reference Section", "New Arrivals"]

    for i, book in enumerate(books):
        num_copies = random.randint(2, 5)
        for j in range(num_copies):
            copy = BookCopy(
                book_id=book.id,
                accession_number=f"ACC-{(i+1):03d}-{(j+1):02d}",
                barcode=f"LIB-{(i+1):04d}-{(j+1):03d}",
                status=BookCopyStatus.AVAILABLE,
                location=random.choice(locations),
                condition=random.choice([BookCondition.NEW, BookCondition.GOOD, BookCondition.GOOD, BookCondition.FAIR]),
            )
            copies.append(copy)

    db.add_all(copies)
    db.flush()

    print("📖 Creating borrow records...")

    # Create some active borrows
    available_copies = [c for c in copies if c.status == BookCopyStatus.AVAILABLE]
    random.shuffle(available_copies)

    borrow_records = []
    for i in range(min(15, len(available_copies))):
        student = random.choice(students)
        copy = available_copies[i]
        days_ago = random.randint(1, 20)
        borrowed_at = datetime.utcnow() - timedelta(days=days_ago)
        due_date = borrowed_at + timedelta(days=14)

        status = BorrowStatus.ACTIVE
        returned_at = None

        # Some returned, some overdue
        if i < 5:  # Active
            copy.status = BookCopyStatus.BORROWED
        elif i < 10:  # Returned
            status = BorrowStatus.RETURNED
            returned_at = borrowed_at + timedelta(days=random.randint(7, 16))
            copy.status = BookCopyStatus.AVAILABLE
        else:  # Overdue (borrowed long ago)
            borrowed_at = datetime.utcnow() - timedelta(days=random.randint(20, 30))
            due_date = borrowed_at + timedelta(days=14)
            copy.status = BookCopyStatus.BORROWED

        record = BorrowRecord(
            user_id=student.id, book_copy_id=copy.id,
            borrowed_at=borrowed_at, due_date=due_date,
            returned_at=returned_at, status=status,
            renewal_count=random.randint(0, 1),
        )
        borrow_records.append(record)

    db.add_all(borrow_records)
    db.flush()

    print("Creating reviews...")

    reviews = []
    review_pairs = set()
    for _ in range(40):
        student = random.choice(students)
        book = random.choice(books)
        pair = (student.id, book.id)
        if pair in review_pairs:
            continue
        review_pairs.add(pair)

        review = Review(
            user_id=student.id, book_id=book.id,
            rating=round(random.uniform(3.0, 5.0), 1),
            review_text=random.choice([
                "Excellent book! Highly recommended for anyone interested in the subject.",
                "Very informative and well-written. A must-read.",
                "Good book but some sections could be more detailed.",
                "Great reference material. I keep coming back to it.",
                "Changed my perspective on the subject. Brilliant writing.",
                "Solid content but a bit dry in places.",
                "One of the best books I've read in this field.",
                "Comprehensive and well-structured. Perfect for students.",
                None,
            ]),
        )
        reviews.append(review)
        if len(reviews) >= 30:
            break

    for review in reviews:
        db.add(review)
    db.flush()

    print("🔔 Creating notifications...")

    notifications = []
    for student in students[:5]:
        notifications.append(Notification(
            user_id=student.id,
            type=NotificationType.GENERAL,
            title="Welcome to the Library!",
            message="Welcome to our university library system. Explore our collection and start borrowing!",
        ))

    db.add_all(notifications)
    db.commit()

    print(f"""
✅ Seed data created successfully!

📊 Summary:
   • Users: {3 + len(students)} (3 staff + {len(students)} students)
   • Books: {len(books)}
   • Book Copies: {len(copies)}
   • Categories: {len(categories)}
   • Authors: {len(authors)}
   • Publishers: {len(publishers)}
   • Borrow Records: {len(borrow_records)}
   • Reviews: {len(reviews)}

🔑 Login credentials:
   • Admin:     admin@library.edu / admin123
   • Librarian: sarah@library.edu / librarian123
   • Student:   vishnu@university.edu / student123
   • (All students use password: student123)
""")

    db.close()


if __name__ == "__main__":
    seed()
