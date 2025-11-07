# base/models.py

from django.db import models


class CreatedUpdatedBase(models.Model):
    """
    An abstract base class model that provides self-updating `created` and
    `updated` fields.
    """

    created = models.DateTimeField(
        "Created",
        auto_now_add=True,
        help_text="The date and time this object was created.",
    )
    updated = models.DateTimeField(
        "Updated",
        auto_now=True,
        help_text="The date and time this object was last updated.",
    )

    class Meta:
        abstract = True


class Note(CreatedUpdatedBase):
    """
    A note.

    NOTE:
    This is an abstract base class for notes. If a `user` field is needed,
    it should be added in the child class. This class provides common fields
    and methods that can be reused in different note models.
    """

    title = models.CharField(
        "Title",
        max_length=255,
        help_text="The title of this note.",
    )
    content = models.TextField(
        "Content",
        help_text="The content of this note.",
        blank=True,
    )
    url = models.URLField(
        "URL",
        help_text="A reference URL for this note.",
        blank=True,
    )
    main_image = models.ImageField(
        verbose_name="Main Image",
        help_text="Add an image for the note.",
        # `upload_to` is a required argument for `ImageField`.
        # It specifies the path to which the uploaded file will be saved.
        upload_to="test_uploads/",
        blank=True,
        null=True,
    )

    def display_content(self):
        """
        This function returns a truncated version of the note's content.
        This can be used in the admin panel and other places where the full
        content is not needed.
        """
        return self.content[:30] + ("..." if len(self.content) > 30 else "")

    def __str__(self):
        return (
            f"{self.title} - {self.content[:50]}"
            f"{'...' if len(self.content) > 50 else ''}"
        )

    class Meta:
        # Use `abstract = True` to make this model an abstract base class which doesn't
        # have a model table created in the database.
        abstract = True
        # `verbose_name` and `verbose_name_plural` and `ordering` are declared in the
        # child class.
